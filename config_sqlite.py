"""
SQLite configuration for testing (alternative to MySQL)
"""
import os

# Database Configuration - SQLite version for testing
DB_CONFIG = {
    'database': os.getenv('DB_NAME', 'sky_hr_payslips.db'),
    'timeout': 30
}

# Auto-upload service configuration
AUTO_START = os.getenv('AUTO_START', 'true').lower() == 'true'

# Application settings
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# File processing settings
EXCEL_POLL_INTERVAL = int(os.getenv('EXCEL_POLL_INTERVAL', '30'))  # seconds
PDF_POLL_INTERVAL = int(os.getenv('PDF_POLL_INTERVAL', '60'))      # seconds
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))                   # records per batch

# Database table names
TABLE_EMPLOYEES = 'employees'
TABLE_PROCESSED_FILES = 'processed_files'
TABLE_LOGIN_ATTEMPTS = 'login_attempts'
