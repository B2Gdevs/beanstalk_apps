# Beanstalk Novel Tools

A full-stack FastAPI application with React frontend, designed for novel writing and project management tools.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Python 3.10+
- uv (Python package manager)

### Setup
1. **Start the database**:
   ```bash
   cd beanstalk_notion_service
   docker compose up db -d
   ```

2. **Set up the backend**:
   ```bash
   cd beanstalk_notion_service/backend
   uv sync
   source .venv/bin/activate
   alembic upgrade head
   python -c "from app.initial_data import init; init()"
   ```

3. **Run the backend**:
   ```bash
   ./run_backend.sh
   ```

4. **Access the API**: http://localhost:8000/docs

## 📚 Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Complete setup instructions
- **[API Usage Guide](docs/API_USAGE_GUIDE.md)** - How to use the API
- **[Documentation Index](docs/README.md)** - All available docs

## 🏗️ Project Structure

```
beanstalk_novel_tools/
├── docs/                          # Documentation
├── run_backend.sh                # Backend startup script
└── beanstalk_notion_service/     # Main application
    ├── backend/                  # FastAPI backend
    ├── frontend/                 # React frontend
    ├── docker-compose.yml        # Docker services
    └── .env                      # Environment variables
```

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM
- **PostgreSQL** - Database
- **Alembic** - Database migrations
- **uv** - Python package management

### Frontend
- **React** - Frontend framework
- **TypeScript** - Type safety
- **Vite** - Build tool

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 🔐 Default Credentials

- **Email**: `admin@example.com`
- **Password**: `changethis`

⚠️ **Change these in production!**

## 🛠️ Development

### Backend Development
```bash
cd beanstalk_notion_service/backend
source .venv/bin/activate
fastapi run app/main.py --reload
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Testing
```bash
cd beanstalk_notion_service/backend
source .venv/bin/activate
python -m pytest
```

## 🐳 Docker Services

- **db** - PostgreSQL database
- **backend** - FastAPI application
- **frontend** - React application
- **adminer** - Database administration

## 🧪 Quick Test - Notion API

Want to test the Notion integration right now? Here's the fastest way:

1. **Start the server**: `./run_backend.sh`
2. **Open Swagger UI**: http://localhost:8000/docs
3. **Click "Authorize"** → Enter `admin@example.com` / `changethis`
4. **Find "notion" section** → `POST /api/v1/notion/test-print`
5. **Click "Try it out"** → Enter any Notion URL → **Click "Execute"**
6. **Check your terminal** - you'll see the page content printed!

📚 **Full testing guide**: [docs/TESTING_NOTION_API.md](docs/TESTING_NOTION_API.md)

## 📡 API Endpoints

### Authentication
- `POST /api/v1/login/access-token` - Get access token
- `POST /api/v1/login/test-token` - Test token

### Users
- `GET /api/v1/users/` - List users (superuser only)
- `POST /api/v1/users/` - Create user (superuser only)
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user

### Items
- `GET /api/v1/items/` - List items
- `POST /api/v1/items/` - Create item
- `GET /api/v1/items/{id}` - Get item
- `PATCH /api/v1/items/{id}` - Update item
- `DELETE /api/v1/items/{id}` - Delete item

### Notion Integration
- `POST /api/v1/notion/read-page` - Read Notion page content
- `POST /api/v1/notion/test-print` - Test endpoint (prints to terminal)
- `GET /api/v1/notion/extract-page-id` - Extract page ID from URL
- `GET /api/v1/notion/health` - Check Notion API configuration

### Utilities
- `GET /api/v1/utils/health-check/` - Health check
- `POST /api/v1/utils/test-email/` - Send test email (superuser only)

## 🔗 Useful Links

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/utils/health-check/

## 🚨 Troubleshooting

### Common Issues

1. **Database connection error**: Make sure Docker is running and the database container is healthy
2. **Port already in use**: Kill the process using port 8000
3. **Module not found**: Recreate the virtual environment with `uv sync`
4. **Migration errors**: Run `alembic upgrade head`

See the [Setup Guide](docs/SETUP_GUIDE.md) for detailed troubleshooting steps.

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Happy Coding! 🎉**
