# API Usage Guide - Swagger UI

This guide explains how to use the FastAPI backend API through Swagger UI.

> **📋 Prerequisites**: Make sure you've completed the setup process first. See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed setup instructions.

## 🚀 Getting Started

### 1. Start the Backend Server

From the project root, run:
```bash
./run_backend.sh
```

The server will start at: **http://localhost:8000**

> **💡 Note**: If you encounter database connection errors, make sure the PostgreSQL database is running. See the [Setup Guide](./SETUP_GUIDE.md) for troubleshooting.

### 2. Access Swagger UI

Open your browser and go to: **http://localhost:8000/docs**

You'll see the Swagger UI interface with all available API endpoints.

## 🔐 Authentication

The API uses OAuth2 with Bearer tokens for authentication. Most endpoints require authentication.

### Default Superuser Credentials

The system creates a default superuser with these credentials:
- **Email:** `admin@example.com`
- **Password:** `changethis`

⚠️ **Security Note:** These are default credentials for development only. Change them in production!

### How to Authenticate

1. **Click the "Authorize" button** (green button with lock icon) in the top-right of Swagger UI
2. **Enter your credentials:**
   - **Username:** `admin@example.com`
   - **Password:** `changethis`
   - Leave other fields empty
3. **Click "Authorize"**
4. **Click "Close"**

You're now authenticated! The lock icons next to protected endpoints will be unlocked.

## 📋 Available API Endpoints

### 🔑 Authentication Endpoints (`/login`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/login/access-token` | Get access token | No |
| POST | `/api/v1/login/test-token` | Test current token | Yes |
| POST | `/api/v1/password-recovery/{email}` | Request password reset | No |
| POST | `/api/v1/reset-password/` | Reset password with token | No |

### 👥 User Management (`/users`)

| Method | Endpoint | Description | Auth Required | Superuser Only |
|--------|----------|-------------|---------------|----------------|
| GET | `/api/v1/users/` | List all users | Yes | ✅ |
| POST | `/api/v1/users/` | Create new user | Yes | ✅ |
| GET | `/api/v1/users/me` | Get current user info | Yes | No |
| PATCH | `/api/v1/users/me` | Update current user | Yes | No |
| PATCH | `/api/v1/users/{id}` | Update user by ID | Yes | ✅ |
| DELETE | `/api/v1/users/{id}` | Delete user | Yes | ✅ |

### 📦 Items Management (`/items`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/items/` | List items (own or all if superuser) | Yes |
| POST | `/api/v1/items/` | Create new item | Yes |
| GET | `/api/v1/items/{id}` | Get item by ID | Yes |
| PATCH | `/api/v1/items/{id}` | Update item | Yes |
| DELETE | `/api/v1/items/{id}` | Delete item | Yes |

### 🛠️ Utility Endpoints (`/utils`)

| Method | Endpoint | Description | Auth Required | Superuser Only |
|--------|----------|-------------|---------------|----------------|
| GET | `/api/v1/utils/health-check/` | Health check | No | No |
| POST | `/api/v1/utils/test-email/` | Send test email | Yes | ✅ |

### 🔒 Private Endpoints (`/private`) - Local Development Only

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/private/users/` | Create user (private) | No |

## 🎯 Common Usage Examples

### 1. Get an Access Token

**Endpoint:** `POST /api/v1/login/access-token`

**Request Body (form-data):**
```
username: admin@example.com
password: changethis
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Get Current User Info

**Endpoint:** `GET /api/v1/users/me`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "admin@example.com",
  "is_active": true,
  "is_superuser": true,
  "full_name": null
}
```

### 3. Create a New User (Superuser Only)

**Endpoint:** `POST /api/v1/users/`

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "full_name": "New User",
  "is_superuser": false,
  "is_active": true
}
```

### 4. Create a New Item

**Endpoint:** `POST /api/v1/items/`

**Request Body:**
```json
{
  "title": "My First Item",
  "description": "This is a test item"
}
```

### 5. List All Items

**Endpoint:** `GET /api/v1/items/`

**Query Parameters:**
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 100)

## 🔧 Testing the API

### Using Swagger UI

1. **Authenticate first** using the "Authorize" button
2. **Click on any endpoint** to expand it
3. **Click "Try it out"**
4. **Fill in the required parameters**
5. **Click "Execute"**
6. **View the response** in the Response section

### Using curl (Command Line)

```bash
# Get access token
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis"

# Use the token to access protected endpoints
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 🚨 Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Make sure you're authenticated
   - Check that your token hasn't expired
   - Verify the Authorization header format: `Bearer <token>`

2. **403 Forbidden**
   - The endpoint requires superuser privileges
   - Make sure you're logged in as a superuser

3. **404 Not Found**
   - Check the endpoint URL
   - Make sure the server is running on port 8000

4. **422 Validation Error**
   - Check the request body format
   - Ensure all required fields are provided
   - Verify data types match the expected schema

### Token Expiration

Access tokens expire after a certain time (configurable). If you get authentication errors:
1. Re-authenticate using the "Authorize" button
2. Or get a new token via `/api/v1/login/access-token`

## 📚 Additional Resources

- **OpenAPI Schema:** http://localhost:8000/api/v1/openapi.json
- **ReDoc Documentation:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/v1/utils/health-check/

## 🔒 Security Notes

- Change default passwords in production
- Use HTTPS in production
- Implement proper secret management
- Regularly rotate access tokens
- Monitor API usage and implement rate limiting

---

**Happy API Testing! 🎉**
