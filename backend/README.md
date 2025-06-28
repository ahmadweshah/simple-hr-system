# Simple HR System Backend

A minimal HR system backend built with Django REST Framework, featuring candidate registration, application tracking, and admin management capabilities with S3 file storage and comprehensive API documentation.

## 🚀 Features

### 🎯 Candidate Features
- **Candidate Registration**: Register with personal details and resume upload (PDF/DOCX, max 5MB)
- **Application Status Tracking**: Check current application status and complete history
- **Input Validation**: Comprehensive validation for all fields including file types and duplicates

### 🔐 Admin Features (require `X-ADMIN=1` header)
- **List Candidates**: Paginated, filtered candidate list with sorting
- **Update Status**: Change candidate status with feedback and automatic notifications
- **Download Resume**: Direct S3 resume download with secure access
- **Status History**: Complete audit trail of all status changes

## 🛠 Tech Stack

- **Backend**: Django 5.2 + Django REST Framework 3.16
- **Database**: PostgreSQL (production) / SQLite (development)
- **File Storage**: Amazon S3 via django-storages + boto3
- **API Documentation**: Swagger/OpenAPI via drf-spectacular
- **Package Management**: UV (modern Python package manager)
- **Validation**: python-magic for file type validation
- **Logging**: Comprehensive logging system

## 📋 Requirements

- Python 3.10+
- UV package manager (recommended) or pip
- PostgreSQL (optional, SQLite by default)
- AWS S3 bucket and credentials (optional, local storage by default)

## ⚡ Quick Start

### Option 1: Using UV (Recommended)

```bash
# Clone and navigate to the backend directory
cd /path/to/simple-hr-system/backend

# Run the automated setup script
chmod +x setup.sh
./setup.sh

# Start the development server
uv run python manage.py runserver
```

### Option 2: Manual Setup

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Run migrations
uv run python manage.py migrate

# Create superuser (optional)
uv run python manage.py createsuperuser

# Start server
uv run python manage.py runserver
```

### Option 3: Docker Deployment

```bash
# Development mode (with Django dev server)
./run.sh dev

# Production mode (with Gunicorn)
./run.sh prod

# Or manually with docker-compose
docker-compose up -d                    # Development
docker-compose -f docker-compose.prod.yml up -d  # Production

# Build Docker image only
./run.sh build

# Run tests in Docker
./run.sh test

# Clean up containers and images
./run.sh clean
```

### Option 4: Production with Gunicorn

```bash
# Install dependencies
uv sync

# Set up environment for production
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Run database migrations
uv run python manage.py migrate

# Collect static files
uv run python manage.py collectstatic --noinput

# Start with Gunicorn (production-ready)
uv run gunicorn --config gunicorn.conf.py core.wsgi:application
```

The Gunicorn configuration includes:
- **Multi-worker processing**: Automatically scales workers based on CPU cores
- **Logging**: Comprehensive access and error logging
- **Health monitoring**: Process restart after request limits
- **Security**: Runs as non-root user in Docker

# Or build and run manually
docker build -t hr-system .
docker run -p 8000:8000 hr-system
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://username:password@localhost:5432/hrdb

# AWS S3 Configuration (optional - defaults to local storage)
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### AWS S3 Setup

1. **Create S3 Bucket**:
   ```bash
   aws s3 mb s3://your-hr-system-bucket
   ```

2. **Configure CORS Policy**:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "POST", "PUT"],
       "AllowedOrigins": ["*"],
       "ExposeHeaders": []
     }
   ]
   ```

3. **Set IAM Permissions**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject",
           "s3:PutObject",
           "s3:DeleteObject"
         ],
         "Resource": "arn:aws:s3:::your-hr-system-bucket/*"
       }
     ]
   }
   ```

## 📚 API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔗 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/candidates/` | Register new candidate |
| `GET` | `/api/candidates/{id}/status/` | Check application status |

### Admin Endpoints (require `X-ADMIN=1` header)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/candidates/` | List all candidates (paginated) |
| `PATCH` | `/api/admin/candidates/{id}/status/` | Update candidate status |
| `GET` | `/api/admin/candidates/{id}/resume/` | Download candidate resume |

### Example Usage

#### Register a Candidate

```bash
curl -X POST http://localhost:8000/api/candidates/ \
  -H "Content-Type: multipart/form-data" \
  -F "full_name=John Doe" \
  -F "email=john.doe@example.com" \
  -F "phone=+1234567890" \
  -F "date_of_birth=1990-01-15" \
  -F "years_of_experience=5" \
  -F "department=IT" \
  -F "resume=@/path/to/resume.pdf"
```

#### Check Application Status

```bash
curl -X GET http://localhost:8000/api/candidates/{candidate-id}/status/
```

#### Update Status (Admin)

```bash
curl -X PATCH http://localhost:8000/api/admin/candidates/{candidate-id}/status/ \
  -H "X-ADMIN: 1" \
  -H "Content-Type: application/json" \
  -d '{"status": "under_review", "feedback": "Application under review"}'
```

#### List Candidates (Admin)

```bash
curl -X GET "http://localhost:8000/api/admin/candidates/?department=IT&page=1" \
  -H "X-ADMIN: 1"
```

## 🧪 Testing

### Run the Test Suite

```bash
# Install test dependencies and run
uv run python test_api.py

# Or run Django tests
uv run python manage.py test
```

### Manual Testing

The `test_api.py` script provides comprehensive testing of all endpoints:

```bash
uv run python test_api.py
```

## 📊 Database Schema

### Candidate Model
- `id` (UUID, Primary Key)
- `full_name` (CharField, max_length=255)
- `email` (EmailField, unique)
- `phone` (CharField, max_length=20, unique)
- `date_of_birth` (DateField)
- `years_of_experience` (PositiveIntegerField)
- `department` (Choice: IT, HR, Finance)
- `resume` (FileField, S3 storage)
- `current_status` (Choice: submitted, under_review, interview_scheduled, rejected, accepted)
- `created_at` (DateTimeField, auto_now_add)
- `updated_at` (DateTimeField, auto_now)

### StatusHistory Model
- `candidate` (ForeignKey to Candidate)
- `status` (CharField)
- `feedback` (TextField, optional)
- `changed_at` (DateTimeField, auto_now_add)
- `admin_info` (CharField, optional)

## 🏗 Project Structure

```
backend/
├── core/                  # Django project settings
│   ├── settings.py       # Main configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI application
├── candidates/           # Candidate management app
│   ├── models.py        # Database models
│   ├── serializers.py   # API serializers
│   ├── views.py         # API views
│   ├── urls.py          # App URL routing
│   └── admin.py         # Django admin interface
├── common/              # Shared utilities
│   ├── middleware.py    # Custom middleware
│   ├── permissions.py   # Custom permissions
│   └── utils.py         # Utility functions
├── manage.py            # Django management script
├── pyproject.toml       # UV dependencies
├── requirements.txt     # Pip dependencies
├── docker-compose.yml   # Docker setup
├── Dockerfile          # Docker image
├── setup.sh            # Automated setup script
├── test_api.py         # API testing script
└── .env.example        # Environment template
```

## 🔧 Development

### Code Quality

```bash
# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8 .

# Run tests
uv run pytest
```

### Database Management

```bash
# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Load sample data
uv run python manage.py loaddata fixtures/sample_data.json
```

## 🚀 Production Deployment

### Environment Setup

```bash
# Set production environment variables
export DEBUG=False
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:pass@host:port/db
export USE_S3=True
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Using Gunicorn

```bash
# Install production server
uv add gunicorn

# Run with Gunicorn
uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

```bash
# Build production image
docker build -t hr-system:prod .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Features

- **Input Validation**: Comprehensive validation for all inputs
- **File Type Validation**: Magic number validation for uploaded files
- **Size Limits**: 5MB maximum file size for resumes
- **Admin Authentication**: Header-based admin access control
- **CORS Configuration**: Configurable cross-origin resource sharing
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **XSS Protection**: Django's built-in XSS protection

## 📈 Performance Optimizations

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Pagination**: Built-in pagination for large datasets
- **Query Optimization**: Efficient database queries with select_related
- **File Storage**: S3 integration for scalable file storage
- **Caching**: Ready for Redis caching integration

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   uv run python manage.py runserver 8001
   ```

2. **Database connection error**:
   ```bash
   # Check DATABASE_URL in .env
   uv run python manage.py dbshell
   ```

3. **S3 permission denied**:
   ```bash
   # Verify AWS credentials and bucket permissions
   aws s3 ls s3://your-bucket-name
   ```

4. **File upload fails**:
   ```bash
   # Check file size and type
   file your-resume.pdf
   ```

## 📝 License

MIT License - feel free to use this project for your applications.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the API documentation at `/swagger/`
- Review the troubleshooting section
- Check Django and DRF documentation
- Create an issue in the repository

---

**🎉 Your HR System is ready to go!** Visit http://localhost:8000/swagger/ to start exploring the API.
