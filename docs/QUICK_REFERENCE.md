# Quick Reference

Common commands and shortcuts for the Beanstalk Novel Tools project.

## 🚀 Essential Commands

### Start Everything
```bash
# Start database
cd beanstalk_notion_service && docker compose up db -d

# Start backend
./run_backend.sh
```

### Backend Development
```bash
# Activate virtual environment
cd beanstalk_notion_service/backend
source .venv/bin/activate

# Run with auto-reload
fastapi run app/main.py --reload

# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=app
```

### Database Operations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Create initial data
python -c "from app.initial_data import init; init()"
```

### Docker Commands
```bash
# Start database only
docker compose up db -d

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove data
docker compose down -v

# Check service status
docker compose ps
```

## 🔗 Important URLs

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/utils/health-check/
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Default Credentials

- **Email**: `admin@example.com`
- **Password**: `changethis`

## 📁 Key Files

- `run_backend.sh` - Backend startup script
- `beanstalk_notion_service/.env` - Environment variables
- `beanstalk_notion_service/docker-compose.yml` - Docker services
- `beanstalk_notion_service/backend/app/models.py` - Database models
- `beanstalk_notion_service/backend/app/api/` - API endpoints

## 🛠️ Environment Variables

Key variables in `.env`:
```bash
POSTGRES_PASSWORD=changethis
SECRET_KEY=changethis
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
```

## 🚨 Quick Fixes

### Database Connection Error
```bash
docker compose up db -d
# Wait for healthy status
docker compose ps
```

### Port Already in Use
```bash
lsof -i :8000
kill -9 <PID>
```

### Virtual Environment Issues
```bash
cd beanstalk_notion_service/backend
rm -rf .venv
uv sync
source .venv/bin/activate
```

### Migration Issues
```bash
alembic upgrade head
```

## 📋 Project Structure

```
beanstalk_novel_tools/
├── docs/                    # Documentation
├── run_backend.sh          # Backend script
└── beanstalk_notion_service/
    ├── backend/            # FastAPI app
    ├── frontend/           # React app
    ├── docker-compose.yml  # Docker services
    └── .env               # Environment config
```

---

**Need more details?** Check the full [Setup Guide](./SETUP_GUIDE.md) and [API Usage Guide](./API_USAGE_GUIDE.md).
