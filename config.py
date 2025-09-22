"""
Database configuration for SKY HR Payslip System
"""
import os

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'sky_hr_payslips'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'autocommit': True,
    'pool_name': 'sky_hr_pool',
    'pool_size': 5
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
