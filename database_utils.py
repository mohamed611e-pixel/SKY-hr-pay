"""
Database utilities for SKY HR Payslip System
"""
import mysql.connector
from mysql.connector import Error, pooling
import logging
from typing import Dict, List, Optional, Any, Tuple
from config import DB_CONFIG, TABLE_EMPLOYEES, TABLE_PROCESSED_FILES, TABLE_LOGIN_ATTEMPTS

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and operations manager"""

    def __init__(self):
        self.connection_pool = None
        self.initialize_pool()

    def initialize_pool(self):
        """Initialize database connection pool"""
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=DB_CONFIG['pool_name'],
                pool_size=DB_CONFIG['pool_size'],
                **{k: v for k, v in DB_CONFIG.items() if k not in ['pool_name', 'pool_size', 'autocommit']}
            )
            logger.info("Database connection pool initialized successfully")
        except Error as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.connection_pool.get_connection()
        except Error as e:
            logger.error(f"Failed to get database connection: {e}")
            raise

    def initialize_database(self):
        """Initialize database tables"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create employees table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_EMPLOYEES} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hrid VARCHAR(50) UNIQUE NOT NULL,
                    nid VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_hrid (hrid),
                    INDEX idx_nid (nid),
                    INDEX idx_name (name)
                )
            """)

            # Create processed_files table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_PROCESSED_FILES} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) UNIQUE NOT NULL,
                    file_type ENUM('excel', 'pdf') NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status ENUM('success', 'failed', 'partial') NOT NULL,
                    records_processed INT DEFAULT 0,
                    error_message TEXT,
                    INDEX idx_filename (filename),
                    INDEX idx_processed_at (processed_at)
                )
            """)

            # Create login_attempts table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_LOGIN_ATTEMPTS} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hrid VARCHAR(50),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    INDEX idx_hrid (hrid),
                    INDEX idx_attempted_at (attempted_at)
                )
            """)

            conn.commit()
            logger.info("Database tables initialized successfully")

        except Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_employee(self, hrid: str) -> Optional[Dict[str, Any]]:
        """Get employee by HRID"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {TABLE_EMPLOYEES} WHERE hrid = %s", (hrid,))
            result = cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"Failed to get employee {hrid}: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_employee_by_nid(self, nid: str) -> Optional[Dict[str, Any]]:
        """Get employee by National ID"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {TABLE_EMPLOYEES} WHERE nid = %s", (nid,))
            result = cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"Failed to get employee by NID {nid}: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_all_employees(self) -> Dict[str, Dict[str, str]]:
        """Get all employees as dictionary for fast lookup"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT hrid, nid, name FROM {TABLE_EMPLOYEES}")
            results = cursor.fetchall()

            employees = {}
            for row in results:
                employees[row['hrid']] = {
                    'NID': row['nid'],
                    'Name': row['name']
                }
            return employees
        except Error as e:
            logger.error(f"Failed to get all employees: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def insert_employee(self, hrid: str, nid: str, name: str, department: str = None, position: str = None) -> bool:
        """Insert new employee"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {TABLE_EMPLOYEES} (hrid, nid, name, department, position)
                VALUES (%s, %s, %s, %s, %s)
            """, (hrid, nid, name, department, position))
            conn.commit()
            logger.info(f"Employee {hrid} inserted successfully")
            return True
        except Error as e:
            logger.error(f"Failed to insert employee {hrid}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def update_employee(self, hrid: str, nid: str = None, name: str = None, department: str = None, position: str = None) -> bool:
        """Update employee information"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Build dynamic update query
            updates = []
            values = []
            if nid is not None:
                updates.append("nid = %s")
                values.append(nid)
            if name is not None:
                updates.append("name = %s")
                values.append(name)
            if department is not None:
                updates.append("department = %s")
                values.append(department)
            if position is not None:
                updates.append("position = %s")
                values.append(position)

            if not updates:
                return True

            values.append(hrid)
            query = f"UPDATE {TABLE_EMPLOYEES} SET {', '.join(updates)} WHERE hrid = %s"

            cursor.execute(query, tuple(values))
            conn.commit()
            logger.info(f"Employee {hrid} updated successfully")
            return True
        except Error as e:
            logger.error(f"Failed to update employee {hrid}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def bulk_insert_employees(self, employees: List[Tuple[str, str, str, str, str]]) -> Tuple[int, int]:
        """Bulk insert employees with transaction support"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            successful = 0
            failed = 0

            for hrid, nid, name, department, position in employees:
                try:
                    cursor.execute(f"""
                        INSERT INTO {TABLE_EMPLOYEES} (hrid, nid, name, department, position)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        nid = VALUES(nid),
                        name = VALUES(name),
                        department = VALUES(department),
                        position = VALUES(position),
                        updated_at = CURRENT_TIMESTAMP
                    """, (hrid, nid, name, department, position))
                    successful += 1
                except Error as e:
                    logger.error(f"Failed to insert employee {hrid}: {e}")
                    failed += 1

            conn.commit()
            logger.info(f"Bulk insert completed: {successful} successful, {failed} failed")
            return successful, failed

        except Error as e:
            logger.error(f"Failed to perform bulk insert: {e}")
            return 0, len(employees)
        finally:
            if conn:
                conn.close()

    def log_login_attempt(self, hrid: str, ip_address: str, user_agent: str, success: bool) -> bool:
        """Log login attempt for security monitoring"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {TABLE_LOGIN_ATTEMPTS} (hrid, ip_address, user_agent, success)
                VALUES (%s, %s, %s, %s)
            """, (hrid, ip_address, user_agent, success))
            conn.commit()
            return True
        except Error as e:
            logger.error(f"Failed to log login attempt: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_login_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get login statistics for the specified time period"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # Get total attempts
            cursor.execute(f"""
                SELECT COUNT(*) as total_attempts,
                       SUM(success = 1) as successful_attempts,
                       SUM(success = 0) as failed_attempts
                FROM {TABLE_LOGIN_ATTEMPTS}
                WHERE attempted_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
            """, (hours,))
            result = cursor.fetchone()

            return {
                'total_attempts': result['total_attempts'] or 0,
                'successful_attempts': result['successful_attempts'] or 0,
                'failed_attempts': result['failed_attempts'] or 0,
                'success_rate': (result['successful_attempts'] or 0) / max(result['total_attempts'] or 1, 1) * 100
            }
        except Error as e:
            logger.error(f"Failed to get login stats: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def disconnect(self):
        """Close all database connections"""
        try:
            if self.connection_pool:
                self.connection_pool._remove_connections()
            logger.info("Database connections closed")
        except Error as e:
            logger.error(f"Error closing database connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()
