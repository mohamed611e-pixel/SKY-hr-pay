"""
SQLite database utilities for SKY HR Payslip System (for testing)
"""
import sqlite3
import logging
from typing import Dict, List, Optional, Any, Tuple
from config_sqlite import DB_CONFIG, TABLE_EMPLOYEES, TABLE_PROCESSED_FILES, TABLE_LOGIN_ATTEMPTS

logger = logging.getLogger(__name__)

class DatabaseManager:
    """SQLite database connection and operations manager"""

    def __init__(self):
        self.connection = None
        self.initialize_database()

    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(DB_CONFIG['database'])
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def initialize_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Create employees table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_EMPLOYEES} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hrid TEXT UNIQUE NOT NULL,
                    nid TEXT NOT NULL,
                    name TEXT NOT NULL,
                    department TEXT,
                    position TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create processed_files table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_PROCESSED_FILES} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    file_type TEXT NOT NULL,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    records_processed INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)

            # Create login_attempts table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_LOGIN_ATTEMPTS} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hrid TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL
                )
            """)

            # Create indexes for better performance
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_employees_hrid ON {TABLE_EMPLOYEES}(hrid)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_employees_nid ON {TABLE_EMPLOYEES}(nid)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_login_attempts_hrid ON {TABLE_LOGIN_ATTEMPTS}(hrid)")

            conn.commit()
            logger.info("SQLite database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_employee(self, hrid: str) -> Optional[Dict[str, Any]]:
        """Get employee by HRID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_EMPLOYEES} WHERE hrid = ?", (hrid,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get employee {hrid}: {e}")
            return None

    def get_employee_by_nid(self, nid: str) -> Optional[Dict[str, Any]]:
        """Get employee by National ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_EMPLOYEES} WHERE nid = ?", (nid,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get employee by NID {nid}: {e}")
            return None

    def get_all_employees(self) -> Dict[str, Dict[str, str]]:
        """Get all employees as dictionary for fast lookup"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT hrid, nid, name FROM {TABLE_EMPLOYEES}")
            results = cursor.fetchall()

            employees = {}
            for row in results:
                employees[row['hrid']] = {
                    'NID': row['nid'],
                    'Name': row['name']
                }
            return employees
        except Exception as e:
            logger.error(f"Failed to get all employees: {e}")
            return {}

    def insert_employee(self, hrid: str, nid: str, name: str, department: str = None, position: str = None) -> bool:
        """Insert new employee"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT OR REPLACE INTO {TABLE_EMPLOYEES} (hrid, nid, name, department, position, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (hrid, nid, name, department, position))
            conn.commit()
            logger.info(f"Employee {hrid} inserted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to insert employee {hrid}: {e}")
            return False

    def bulk_insert_employees(self, employees: List[Tuple[str, str, str, str, str]]) -> Tuple[int, int]:
        """Bulk insert employees with transaction support"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            successful = 0
            failed = 0

            for hrid, nid, name, department, position in employees:
                try:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {TABLE_EMPLOYEES} (hrid, nid, name, department, position, updated_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (hrid, nid, name, department, position))
                    successful += 1
                except Exception as e:
                    logger.error(f"Failed to insert employee {hrid}: {e}")
                    failed += 1

            conn.commit()
            logger.info(f"Bulk insert completed: {successful} successful, {failed} failed")
            return successful, failed

        except Exception as e:
            logger.error(f"Failed to perform bulk insert: {e}")
            return 0, len(employees)

    def log_login_attempt(self, hrid: str, ip_address: str, user_agent: str, success: bool) -> bool:
        """Log login attempt for security monitoring"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {TABLE_LOGIN_ATTEMPTS} (hrid, ip_address, user_agent, success)
                VALUES (?, ?, ?, ?)
            """, (hrid, ip_address, user_agent, success))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to log login attempt: {e}")
            return False

    def get_login_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get login statistics for the specified time period"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # Get total attempts
            cursor.execute(f"""
                SELECT COUNT(*) as total_attempts,
                       SUM(success = 1) as successful_attempts,
                       SUM(success = 0) as failed_attempts
                FROM {TABLE_LOGIN_ATTEMPTS}
                WHERE attempted_at >= datetime('now', '-' || ? || ' hours')
            """, (hours,))
            result = cursor.fetchone()

            return {
                'total_attempts': result['total_attempts'] or 0,
                'successful_attempts': result['successful_attempts'] or 0,
                'failed_attempts': result['failed_attempts'] or 0,
                'success_rate': (result['successful_attempts'] or 0) / max(result['total_attempts'] or 1, 1) * 100
            }
        except Exception as e:
            logger.error(f"Failed to get login stats: {e}")
            return {}

    def disconnect(self):
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Global database manager instance
db_manager = DatabaseManager()
