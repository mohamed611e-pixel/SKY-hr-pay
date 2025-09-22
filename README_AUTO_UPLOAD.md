# Automatic Upload System for SKY HRT Solutions

## Overview

The Automatic Upload System enables seamless, hands-free processing of Excel employee data files and PDF payslips without requiring manual admin intervention. The system monitors the `uploaded_payslips/` directory and automatically processes any new files placed there.

## Features

### 🚀 Automatic File Processing
- **Excel Files**: Automatically parses `.xlsx` and `.xlsm` files containing employee data
- **PDF Files**: Validates and organizes payslip PDFs with proper naming conventions
- **Real-time Monitoring**: Continuous background monitoring of upload directory
- **Database Integration**: Automatic synchronization with MySQL database

### 📁 File Organization
- **Input**: Files placed in `uploaded_payslips/` directory
- **Processed**: Valid files moved to `uploaded_payslips/processed/`
- **Invalid**: Problematic files moved to `uploaded_payslips/invalid/` with error logging

### 🗄️ Database Integration
- **Persistent Storage**: Employee data stored in MySQL database
- **Automatic Sync**: In-memory cache synchronized with database
- **Fast Access**: Quick employee lookups for login validation

### 🔧 Configuration Options
- **Enable/Disable**: Set `AUTO_UPLOAD=true/false` environment variable
- **Database Settings**: Configure connection in `config.py`
- **Processing Intervals**: Adjust file check frequency and batch sizes
- **Logging**: Comprehensive logging for monitoring and debugging

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
Update `config.py` with your MySQL database credentials:
```python
DB_CONFIG = {
    'host': 'your-database-host',
    'user': 'your-username',
    'password': 'your-password',
    'database': 'your-database-name',
    'port': 3306
}
```

### 3. Start the Application
```bash
python payslip_site.py
```

## Usage

### Automatic Processing
1. **Excel Files**: Place Excel files with employee data in `uploaded_payslips/`
   - Required columns: "Emp ID", "National ID", "Name"
   - Supported formats: `.xlsx`, `.xlsm`

2. **PDF Files**: Place payslip PDFs with naming convention `Payslip_HRID_MONTH.pdf`
   - Example: `Payslip_EMP001_01.pdf`
   - Files are validated against employee database

3. **Monitoring**: Check processing status via `/auto_upload_status` endpoint

### Manual Upload (Still Available)
- Excel upload: `POST /upload_excel`
- PDF upload: `POST /upload_payslips`
- Manual uploads work alongside automatic processing

## File Processing Flow

```
uploaded_payslips/
├── new_file.xlsx          → Detected by file watcher
├── Payslip_EMP001_01.pdf  → Validated and processed
└── invalid_file.pdf       → Moved to invalid folder

Processing Results:
uploaded_payslips/processed/
├── processed_file.xlsx    → Successfully processed
└── Payslip_EMP001_01.pdf  → Valid payslip

uploaded_payslips/invalid/
└── invalid_file.pdf       → Invalid file with error log
```

## API Endpoints

### Status Monitoring
- `GET /auto_upload_status` - Get auto-upload service status
- Returns: service status, statistics, and error information

### Existing Endpoints (Enhanced)
- `POST /login_employee` - Enhanced with database lookup
- `POST /upload_excel` - Manual Excel upload (still available)
- `POST /upload_payslips` - Manual PDF upload (still available)

## Configuration

### Environment Variables
```bash
# Enable/disable automatic processing
AUTO_UPLOAD=true

# Database configuration
DB_HOST=your-database-host
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database-name

# Admin credentials
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD_HASH=your-password-hash

# Application settings
PORT=5000
DEBUG=false
```

### Configuration File (`config.py`)
```python
# File processing settings
UPLOAD_FOLDER = 'uploaded_payslips'
PROCESSED_FOLDER = 'uploaded_payslips/processed'
INVALID_FOLDER = 'uploaded_payslips/invalid'

# Processing intervals
FILE_CHECK_INTERVAL = 5  # seconds
BATCH_SIZE = 10

# Logging configuration
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'auto_upload.log'
}
```

## Testing

### Run Test Suite
```bash
python test_auto_upload.py
```

### Manual Testing
1. Start the application: `python payslip_site.py`
2. Place test files in `uploaded_payslips/` directory
3. Monitor logs for processing activity
4. Check `/auto_upload_status` for service status

## Logging and Monitoring

### Log Files
- **Console**: Real-time processing logs
- **File**: `auto_upload.log` for persistent logging
- **JSON Format**: Structured logging for easy parsing

### Log Levels
- **INFO**: Normal processing activities
- **WARNING**: Non-critical issues (invalid files, etc.)
- **ERROR**: Processing failures and errors
- **DEBUG**: Detailed debugging information (when enabled)

### Monitoring Dashboard
Access `/auto_upload_status` for real-time statistics:
```json
{
  "enabled": true,
  "status": {
    "is_running": true,
    "processor_stats": {
      "total_employees": 150,
      "processed_files": 25,
      "invalid_files": 3,
      "last_updated": "2024-01-15T10:30:00"
    },
    "pending_files": 0
  }
}
```

## Error Handling

### File Processing Errors
- **Invalid Excel Format**: Files moved to `invalid/` with error details
- **Missing Columns**: Logged with specific column requirements
- **Database Errors**: Automatic retry with exponential backoff
- **File System Errors**: Comprehensive error logging and recovery

### Recovery Mechanisms
- **Automatic Retry**: Failed operations retried automatically
- **Graceful Degradation**: Service continues operating despite individual failures
- **Manual Recovery**: Invalid files can be manually corrected and reprocessed

## Security Considerations

### File Validation
- **Excel Files**: Strict column validation and data type checking
- **PDF Files**: Filename pattern validation and employee verification
- **File Size Limits**: Configurable limits to prevent resource exhaustion

### Database Security
- **Parameterized Queries**: Prevents SQL injection attacks
- **Connection Pooling**: Efficient database connection management
- **Error Sanitization**: Sensitive information filtered from logs

## Troubleshooting

### Common Issues

1. **Service Not Starting**
   - Check database connectivity
   - Verify configuration settings
   - Check application logs for errors

2. **Files Not Processing**
   - Verify file permissions
   - Check file naming conventions
   - Monitor system resources

3. **Database Connection Issues**
   - Verify database credentials
   - Check network connectivity
   - Ensure database server is running

### Debug Mode
Enable debug mode for detailed logging:
```python
DEBUG_MODE = True  # in config.py
```

## Performance Optimization

### Batch Processing
- Files processed in configurable batches
- Database operations optimized for bulk inserts
- Memory usage monitored and controlled

### Caching Strategy
- Employee data cached in memory for fast access
- Database synchronization for consistency
- Cache invalidation on data updates

### Resource Management
- Background threads for non-blocking operation
- Graceful shutdown handling
- Memory leak prevention

## Deployment

### Production Deployment
1. Configure production database settings
2. Set appropriate file permissions
3. Configure logging for production environment
4. Set up monitoring and alerting

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "payslip_site.py"]
```

### Cloud Deployment
- Compatible with Render, Heroku, AWS, etc.
- Environment variable configuration
- Database connectivity requirements

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify configuration settings
3. Test with the provided test suite
4. Check database connectivity and permissions

## Version History

### v1.0.0
- Initial implementation of automatic upload system
- Excel and PDF file processing
- Database integration
- Background service architecture
- Comprehensive error handling and logging
