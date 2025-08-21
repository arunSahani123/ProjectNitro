# File Parser CRUD API

A Django-based REST API for uploading, parsing, and managing files with real-time progress tracking and WebSocket support.

## Features

- **File Upload**: Support for large file uploads with progress tracking
- **File Parsing**: Automatic parsing of CSV, Excel, and PDF files
- **Real-time Updates**: WebSocket integration for live progress updates
- **Authentication**: JWT-based authentication system
- **CRUD Operations**: Complete file management operations
- **Background Processing**: Asynchronous file processing with threading
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Unit Tests**: Comprehensive test coverage

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: PostgreSQL (SQLite for development)
- **Background Tasks**: Python threading
- **Caching**: Django database cache
- **File Processing**: pandas, openpyxl, PyPDF2
- **Documentation**: drf-yasg (Swagger)

## Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite works for development)

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd file-parser-api
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit .env file with your configurations
# For development, the default SQLite settings should work
```

### 5. Install and Start Redis

### 5. Database Setup

```bash
# Create cache table for progress tracking
python manage.py createcachetable

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
### 6. Start the Application

Simply start the Django development server:
```bash
python manage.py runserver
```


### Base URL
```
http://localhost:8000/api/
```

### Authentication

1. **Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

2. **Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### File Operations

3. **Upload a file:**
```bash
curl -X POST http://localhost:8000/api/files/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/your/file.csv"
```

4. **List files:**
```bash
curl -X GET http://localhost:8000/api/files/list/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

5. **Get file progress:**
```bash
curl -X GET http://localhost:8000/api/files/{file_id}/progress/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

6. **Get file content:**
```bash
curl -X GET http://localhost:8000/api/files/{file_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

7. **Delete file:**
```bash
curl -X DELETE http://localhost:8000/api/files/{file_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### WebSocket Connection

Connect to WebSocket for real-time progress updates:
```
ws://localhost:8000/ws/files/{file_id}/
```

## API Documentation

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **JSON Schema**: http://localhost:8000/swagger.json
- **Simple Docs**: http://localhost:8000/api/docs/

## Project Structure

```
file-parser-api/
├── file_parser_project/          # Main Django project
│   ├── __init__.py
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI application
│   ├── asgi.py                  # ASGI application (for WebSocket)
│   └── celery.py                # Celery configuration
├── accounts/                     # User authentication app
│   ├── models.py                # User model
│   ├── serializers.py           # API serializers
│   ├── views.py                 # API views
│   └── urls.py                  # URL routing
├── files/                        # File management app
│   ├── models.py                # File model
│   ├── serializers.py           # API serializers
│   ├── views.py                 # API views
│   ├── tasks.py                 # Celery tasks
│   ├── consumers.py             # WebSocket consumers
│   ├── routing.py               # WebSocket routing
│   └── urls.py                  # URL routing
├── media/                        # Uploaded files
├── logs/                         # Log files
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .env                          # Environment variables
└── manage.py                     # Django management script
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific app tests
python manage.py test files
python manage.py test accounts
```

## File Format Support

### CSV Files
- Automatic delimiter detection
- Headers extraction
- Data preview (first 5 rows)
- Full data access via API

### Excel Files (.xlsx, .xls)
- First sheet parsing
- Column headers
- Data preview and full access
- Pandas-based processing

### PDF Files
- Text extraction from all pages
- Page-by-page content
- Word and character count
- Full text search capability

## Production Deployment

### Using Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual services
docker run -d --name redis redis:alpine
docker run -d --name postgres postgres:13
docker run -d --name file-parser-api your-app:latest
```

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@localhost:5432/proddb
REDIS_URL=redis://localhost:6379/0
```

## Monitoring and Logs

- Application logs: `logs/django.log`
- Celery logs: Console output
- Redis monitoring: `redis-cli monitor`

## Troubleshooting

### Common Issues

1. **File Upload Fails**:
   - Check MAX_FILE_SIZE setting
   - Ensure media directory permissions


### Debug Mode

Enable debug logging by setting in .env:
```env
DEBUG=True
```

## API Response Examples

### File Upload Response
```json
{
  "file_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "File uploaded successfully. Processing started.",
  "status": "uploading",
  "progress": 0
}
```

### File Progress Response
```json
{
  "file_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "progress": 45
}
```

### File Content Response (CSV)
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "data.csv",
  "original_name": "sales_data.csv",
  "status": "ready",
  "content": {
    "type": "csv",
    "headers": ["Date", "Product", "Sales", "Revenue"],
    "rows": 1000,
    "total_rows": 1000,
    "sample_data": [
      {"Date": "2023-01-01", "Product": "Widget A", "Sales": "10", "Revenue": "100.00"},
      {"Date": "2023-01-02", "Product": "Widget B", "Sales": "15", "Revenue": "150.00"}
    ]
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.