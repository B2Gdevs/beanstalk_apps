# Setup Guide - Beanstalk Novel Tools

This guide will walk you through setting up the complete development environment for the Beanstalk Novel Tools project.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Python 3.10+** - [Download here](https://www.python.org/downloads/)
- **uv** (Python package manager) - Will be installed automatically if missing

## 🚀 Quick Start

### 1. Clone and Navigate to Project

```bash
cd /path/to/your/project/beanstalk_novel_tools
```

### 2. Start the Database

The project uses PostgreSQL running in Docker. Start it with:

```bash
cd beanstalk_notion_service
docker compose up db -d
```

Wait for the database to be healthy (about 30 seconds), then verify:

```bash
docker compose ps
```

You should see the database container with status "healthy".

### 3. Set Up Backend Dependencies

```bash
cd beanstalk_notion_service/backend
uv sync
```

This will:
- Create a virtual environment
- Install all Python dependencies
- Set up the project structure

### 4. Run Database Migrations

```bash
source .venv/bin/activate
alembic upgrade head
```

This creates all the necessary database tables.

### 5. Create Initial Data

```bash
python -c "from app.initial_data import init; init()"
```

This creates the default superuser account.

### 6. Start the Backend Server

From the project root:

```bash
./run_backend.sh
```

Or manually:

```bash
cd beanstalk_notion_service/backend
source .venv/bin/activate
fastapi run app/main.py --reload
```

## ✅ Verification

### Check Backend Health

```bash
curl http://localhost:8000/api/v1/utils/health-check/
```

Should return: `true`

### Access API Documentation

Open your browser and go to: **http://localhost:8000/docs**

You should see the Swagger UI interface with all available endpoints.

## 🔐 Default Credentials

The system creates a default superuser with these credentials:

- **Email**: `admin@example.com`
- **Password**: `changethis`

⚠️ **Security Note**: These are default credentials for development only. Change them in production!

## 🗂️ Project Structure

```
beanstalk_novel_tools/
├── docs/                          # Documentation
│   ├── SETUP_GUIDE.md            # This file
│   └── API_USAGE_GUIDE.md        # API usage instructions
├── run_backend.sh                # Backend startup script
└── beanstalk_notion_service/     # Main application
    ├── .env                      # Environment variables
    ├── docker-compose.yml        # Docker services
    ├── backend/                  # FastAPI backend
    │   ├── app/                  # Application code
    │   ├── .venv/               # Virtual environment
    │   └── pyproject.toml       # Python dependencies
    └── frontend/                 # React frontend (optional)
```

## 🐳 Docker Services

The project includes several Docker services:

- **db**: PostgreSQL database
- **adminer**: Database administration tool
- **backend**: FastAPI application
- **frontend**: React frontend
- **prestart**: Database initialization

### Useful Docker Commands

```bash
# Start all services
docker compose up -d

# Start only database
docker compose up db -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v
```

## 🔧 Environment Configuration

The project uses environment variables defined in `beanstalk_notion_service/.env`:

### Key Variables

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis

# Security
SECRET_KEY=changethis
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis

# Environment
ENVIRONMENT=local
```

### Changing Default Passwords

For security, change these values in the `.env` file:

1. `SECRET_KEY` - Used for JWT token signing
2. `POSTGRES_PASSWORD` - Database password
3. `FIRST_SUPERUSER_PASSWORD` - Default admin password

## 🛠️ Development Workflow

### Backend Development

1. **Make code changes** in `beanstalk_notion_service/backend/app/`
2. **The server auto-reloads** when you save files
3. **Test changes** via Swagger UI at http://localhost:8000/docs

### Database Changes

When you modify models in `backend/app/models.py`:

1. **Create migration**:
   ```bash
   cd beanstalk_notion_service/backend
   source .venv/bin/activate
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

### Adding Dependencies

```bash
cd beanstalk_notion_service/backend
uv add package-name
```

## 🧪 Testing

### Run Backend Tests

```bash
cd beanstalk_notion_service/backend
source .venv/bin/activate
python -m pytest
```

### Test Coverage

```bash
python -m pytest --cov=app
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error**: `connection to server at "127.0.0.1", port 5432 failed`

**Solution**:
```bash
cd beanstalk_notion_service
docker compose up db -d
# Wait for database to be healthy
docker compose ps
```

#### 2. Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

#### 3. Virtual Environment Issues

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
cd beanstalk_notion_service/backend
rm -rf .venv
uv sync
source .venv/bin/activate
```

#### 4. Migration Errors

**Error**: `Target database is not up to date`

**Solution**:
```bash
cd beanstalk_notion_service/backend
source .venv/bin/activate
alembic upgrade head
```

#### 5. Docker Issues

**Error**: `Cannot connect to the Docker daemon`

**Solution**:
- Start Docker Desktop
- Wait for it to fully start
- Try the command again

### Getting Help

1. **Check logs**: `docker compose logs -f`
2. **Verify services**: `docker compose ps`
3. **Test connectivity**: `curl http://localhost:8000/api/v1/utils/health-check/`

## 📚 Next Steps

Once setup is complete:

1. **Read the API Usage Guide**: `docs/API_USAGE_GUIDE.md`
2. **Explore the API**: http://localhost:8000/docs
3. **Start developing**: Make changes to the backend code
4. **Test your changes**: Use Swagger UI to test endpoints

## 🔗 Useful Links

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/utils/health-check/
- **Database Admin** (if adminer is running): http://localhost:8080

---

**Happy Coding! 🎉**
