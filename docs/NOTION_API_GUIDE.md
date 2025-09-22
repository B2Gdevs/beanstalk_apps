# Notion API Integration Guide

This guide explains how to use the Notion API integration to read pages from Notion and convert them to markdown format.

## 🔧 Setup

### 1. Get Notion API Key

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "Beanstalk Novel Tools")
4. Select the workspace you want to access
5. Copy the "Internal Integration Token"

### 2. Configure API Key

Add your Notion API key to the environment variables:

**Option 1: Update .env file**
```bash
# In beanstalk_notion_service/.env
NOTION_API_KEY=secret_your_actual_notion_api_key_here
```

**Option 2: Set environment variable**
```bash
export NOTION_API_KEY="secret_your_actual_notion_api_key_here"
```

### 3. Share Pages with Integration

For each Notion page you want to access:

1. Open the page in Notion
2. Click "Share" in the top-right corner
3. Click "Invite" and search for your integration name
4. Click "Invite" to give the integration access

## 📡 API Endpoints

### Read Notion Page

**Endpoint**: `POST /api/v1/notion/read-page`

**Description**: Read a Notion page by URL and return its content as markdown.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
    "page_url": "https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef"
}
```

**Response**:
```json
{
    "page_id": "12345678-90ab-cdef-1234-567890abcdef",
    "title": "Your Page Title",
    "content": "# Your Page Title\n\nThis is the page content...",
    "url": "https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef",
    "properties": {
        "Status": "In Progress",
        "Priority": "High",
        "Tags": ["important", "project"]
    }
}
```

### Extract Page ID

**Endpoint**: `GET /api/v1/notion/extract-page-id`

**Description**: Extract the page ID from a Notion URL without fetching content.

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `page_url`: The Notion page URL

**Example**:
```
GET /api/v1/notion/extract-page-id?page_url=https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef
```

**Response**:
```json
{
    "page_id": "12345678-90ab-cdef-1234-567890abcdef",
    "url": "https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef"
}
```

### Health Check

**Endpoint**: `GET /api/v1/notion/health`

**Description**: Check if the Notion API is properly configured.

**Authentication**: Required (Bearer token)

**Response**:
```json
{
    "status": "healthy",
    "message": "Notion service is properly configured"
}
```

## 🎯 Usage Examples

### Using Swagger UI

1. **Authenticate**: Go to http://localhost:8000/docs and click "Authorize"
2. **Enter credentials**: `admin@example.com` / `changethis`
3. **Find Notion endpoints**: Look for the "notion" section
4. **Test endpoints**: Click "Try it out" and enter a Notion page URL

### Using curl

```bash
# Get access token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Read a Notion page
curl -X POST "http://localhost:8000/api/v1/notion/read-page" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "page_url": "https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef"
  }'

# Extract page ID
curl "http://localhost:8000/api/v1/notion/extract-page-id?page_url=https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef" \
  -H "Authorization: Bearer $TOKEN"

# Check health
curl "http://localhost:8000/api/v1/notion/health" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python

```python
import requests

# Get access token
login_response = requests.post(
    "http://localhost:8000/api/v1/login/access-token",
    data={"username": "admin@example.com", "password": "changethis"}
)
token = login_response.json()["access_token"]

# Read Notion page
headers = {"Authorization": f"Bearer {token}"}
page_response = requests.post(
    "http://localhost:8000/api/v1/notion/read-page",
    headers=headers,
    json={"page_url": "https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef"}
)

page_data = page_response.json()
print(f"Title: {page_data['title']}")
print(f"Content: {page_data['content']}")
```

## 📝 Supported Notion Content Types

The API converts the following Notion block types to markdown:

- **Headings**: `heading_1`, `heading_2`, `heading_3` → `#`, `##`, `###`
- **Text**: `paragraph` → Plain text
- **Lists**: `bulleted_list_item` → `-`, `numbered_list_item` → `1.`
- **Code**: `code` → ```language blocks
- **Quotes**: `quote` → `>`
- **Dividers**: `divider` → `---`
- **To-dos**: `to_do` → `- [ ]` or `- [x]`

## 🔍 Supported URL Formats

The API can extract page IDs from various Notion URL formats:

- `https://www.notion.so/32-character-page-id`
- `https://www.notion.so/workspace/Page-Title-32-character-page-id`
- `https://notion.site/32-character-page-id`
- `https://notion.site/workspace/Page-Title-32-character-page-id`

## 🚨 Error Handling

### Common Errors

**400 Bad Request**:
- Invalid Notion URL format
- Could not extract page ID from URL

**401 Unauthorized**:
- Missing or invalid authentication token
- Notion API key not configured

**403 Forbidden**:
- Notion integration doesn't have access to the page
- Page is private and not shared with integration

**404 Not Found**:
- Page doesn't exist
- Page ID is invalid

**500 Internal Server Error**:
- Notion API request failed
- Unexpected error in processing

### Troubleshooting

1. **"Notion API key not configured"**:
   - Set `NOTION_API_KEY` in your environment
   - Restart the backend server

2. **"Could not extract page ID from URL"**:
   - Check that the URL is a valid Notion page URL
   - Ensure the URL contains a 32-character page ID

3. **"Failed to fetch Notion page"**:
   - Verify the page is shared with your integration
   - Check that the Notion API key is correct
   - Ensure the page exists and is accessible

## 🔒 Security Notes

- **API Key**: Keep your Notion API key secure and never commit it to version control
- **Page Access**: Only pages explicitly shared with your integration will be accessible
- **Rate Limits**: Notion API has rate limits; the service handles them gracefully
- **Authentication**: All endpoints require valid authentication tokens

## 📚 Additional Resources

- [Notion API Documentation](https://developers.notion.com/)
- [Notion Integrations Guide](https://developers.notion.com/docs/getting-started)
- [API Usage Guide](./API_USAGE_GUIDE.md) - General API usage
- [Setup Guide](./SETUP_GUIDE.md) - Project setup instructions

---

**Happy Notion Integration! 📝**
