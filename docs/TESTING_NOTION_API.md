# Testing Notion API - Step-by-Step Guide

This guide will walk you through testing the Notion API integration with real examples and clear instructions.

## 🎯 Quick Test (5 Minutes)

### Step 1: Start Your Backend Server

```bash
# From project root
./run_backend.sh
```

**Expected Output**: Server starts at http://localhost:8000

### Step 2: Open Swagger UI

1. **Open your browser** and go to: http://localhost:8000/docs
2. **Look for the "notion" section** in the API documentation

### Step 3: Authenticate

1. **Click the green "Authorize" button** (top-right corner)
2. **Enter credentials**:
   - Username: `admin@example.com`
   - Password: `changethis`
3. **Click "Authorize"**
4. **Click "Close"**

### Step 4: Test URL Extraction (Debug)

1. **Find the endpoint**: `POST /api/v1/notion/debug-extract`
2. **Click "Try it out"**
3. **Enter your URL** in the request body:
   ```json
   {
     "page_url": "https://www.notion.so/Book-1-Jack-16b9e94d1c9381cea6c4e74c508efea6"
   }
   ```
4. **Click "Execute"**
5. **Check the response** - you should see `"success": true` and the extracted page ID

### Step 5: Test HTTP Client Logging

1. **Find the endpoint**: `GET /api/v1/notion/test-http-client`
2. **Click "Try it out"**
3. **Click "Execute"**
4. **Check your terminal** - you should see comprehensive HTTP request/response logging

### Step 6: Test Book Ingestion

1. **Find the endpoint**: `POST /api/v1/notion/ingest-book`
2. **Click "Try it out"**
3. **Enter your book URL** in the request body:
   ```json
   {
     "page_url": "https://www.notion.so/Book-1-Jack-16b9e94d1c9381cea6c4e74c508efea6"
   }
   ```
4. **Click "Execute"**
5. **Check the response** - you'll see the complete book structure with chapters and pages!
6. **Check your terminal** for detailed ingestion logs

## 🔧 Full Setup Test (10 Minutes)

### Prerequisites Setup

#### 1. Get a Notion API Key

1. **Go to**: https://www.notion.so/my-integrations
2. **Click**: "New integration"
3. **Fill out**:
   - Name: `Beanstalk Test Integration`
   - Workspace: Select your workspace
4. **Click**: "Submit"
5. **Copy the token** (starts with `secret_`)

#### 2. Configure the API Key

**Option A: Update .env file**
```bash
# Edit beanstalk_notion_service/.env
NOTION_API_KEY=secret_your_actual_token_here
```

**Option B: Set environment variable**
```bash
export NOTION_API_KEY="secret_your_actual_token_here"
```

#### 3. Create a Test Page in Notion

1. **Create a new page** in Notion
2. **Add some content**:
   - Title: "Test Page for API"
   - Some text paragraphs
   - A heading or two
   - Maybe a bullet list
3. **Share the page**:
   - Click "Share" (top-right)
   - Click "Invite"
   - Search for "Beanstalk Test Integration"
   - Click "Invite"

#### 4. Get the Page URL

1. **Copy the page URL** from your browser
2. **It should look like**: `https://www.notion.so/workspace/Test-Page-for-API-1234567890abcdef1234567890abcdef`

### Test with Real Notion Page

#### 1. Restart the Backend

```bash
# Stop the current server (Ctrl+C)
# Then restart
./run_backend.sh
```

#### 2. Test the Health Check

1. **Go to**: http://localhost:8000/docs
2. **Find**: `GET /api/v1/notion/health`
3. **Click**: "Try it out" → "Execute"
4. **Expected**: `{"status": "healthy", "message": "Notion service is properly configured"}`

#### 3. Test Page ID Extraction

1. **Find**: `GET /api/v1/notion/extract-page-id`
2. **Click**: "Try it out"
3. **Enter your page URL** in the `page_url` parameter
4. **Click**: "Execute"
5. **Expected**: Returns the page ID and URL

#### 4. Test the Print Endpoint

1. **Find**: `POST /api/v1/notion/test-print`
2. **Click**: "Try it out"
3. **Enter your real page URL**:
   ```json
   {
     "page_url": "https://www.notion.so/workspace/Test-Page-for-API-1234567890abcdef1234567890abcdef"
   }
   ```
4. **Click**: "Execute"
5. **Check your terminal** - you should see the full page content printed!

## 📺 What You'll See in the Terminal

When you run the test-print endpoint, you'll see output like this:

```
================================================================================
🔍 NOTION PAGE TEST - FETCHING PAGE CONTENT
================================================================================
📄 Page ID: 12345678-90ab-cdef-1234-567890abcdef
📝 Title: Test Page for API
🔗 URL: https://www.notion.so/workspace/Test-Page-for-API-1234567890abcdef1234567890abcdef
📊 Properties: 2 found

📋 PAGE PROPERTIES:
----------------------------------------
  • Status: In Progress
  • Priority: High

📖 PAGE CONTENT (156 characters):
----------------------------------------
# Test Page for API

This is a test page for the Notion API integration.

## Features

- Reads Notion pages
- Converts to markdown
- Prints to terminal

## Testing

This page is being used to test the API functionality.
----------------------------------------
✅ END OF PAGE CONTENT
================================================================================
```

## 🚨 Troubleshooting

### "Notion API key not configured"

**Problem**: You see this error in the health check
**Solution**: 
1. Make sure you set `NOTION_API_KEY` in your environment
2. Restart the backend server
3. Test the health endpoint again

### "Could not extract page ID from URL"

**Problem**: The URL format isn't recognized
**Solution**:
1. **Use the debug endpoint first**: `POST /api/v1/notion/debug-extract`
2. **Check the debug output** in your terminal for detailed pattern matching
3. **Make sure you're using a real Notion page URL**
4. **The URL should contain a 32-character page ID**
5. **Try copying the URL directly from your browser**

**Debug Steps**:
```bash
# Test URL extraction with debug endpoint
curl -X POST "http://localhost:8000/api/v1/notion/debug-extract" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"page_url": "YOUR_NOTION_URL"}'
```

### "Failed to fetch Notion page"

**Problem**: API request fails
**Solution**:
1. Check that the page is shared with your integration
2. Verify your API key is correct
3. Make sure the page exists and is accessible

### "401 Unauthorized"

**Problem**: Authentication fails
**Solution**:
1. Make sure you're logged in to Swagger UI
2. Use the correct credentials: `admin@example.com` / `changethis`
3. Click "Authorize" again

## 🎯 Test Scenarios

### Scenario 1: Basic Text Page
- **Create**: A simple page with just text
- **Test**: Should print the text content as markdown

### Scenario 2: Rich Content Page
- **Create**: A page with headings, lists, code blocks
- **Test**: Should convert all content types to markdown

### Scenario 3: Page with Properties
- **Create**: A page with custom properties (Status, Priority, etc.)
- **Test**: Should show properties in the terminal output

### Scenario 4: Long Content Page
- **Create**: A page with lots of content
- **Test**: Should handle large content without issues

## 📊 Expected Results

### Successful Test Response
```json
{
  "status": "success",
  "message": "Page content printed to terminal. Check your server logs.",
  "page_title": "Your Page Title",
  "content_length": 1234,
  "properties_count": 3
}
```

### Terminal Output
- ✅ Clear section headers with emojis
- ✅ Page metadata (ID, title, URL)
- ✅ Properties list (if any)
- ✅ Full content in markdown format
- ✅ Error messages (if something goes wrong)

## 🔄 Next Steps

Once testing is successful:

1. **Try different page types** (databases, different content formats)
2. **Test error handling** (invalid URLs, private pages)
3. **Use the regular endpoints** (`/read-page`) for actual integration
4. **Build your application** using the Notion API

## 📞 Need Help?

- **Check the logs**: Look at your terminal output for detailed error messages
- **Verify setup**: Make sure all prerequisites are completed
- **Test incrementally**: Start with the health check, then page ID extraction, then full content
- **Use Swagger UI**: The interactive documentation makes testing easy

---

**Happy Testing! 🚀**
