"""
Notion API routes for reading pages and content.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.api.deps import CurrentUser
from app.core.notion import NotionPageContent, notion_service

router = APIRouter(prefix="/notion", tags=["notion"])


class NotionPageRequest(BaseModel):
    """Request model for Notion page URL."""
    
    page_url: HttpUrl = Field(..., description="The Notion page URL to read")


class NotionPageResponse(BaseModel):
    """Response model for Notion page content."""
    
    page_id: str = Field(..., description="The Notion page ID")
    title: str = Field(..., description="The page title")
    content: str = Field(..., description="The page content as markdown")
    url: str = Field(..., description="The original Notion page URL")
    properties: dict = Field(..., description="Page properties")


@router.post("/read-page", response_model=NotionPageResponse)
async def read_notion_page(
    request: NotionPageRequest,
    current_user: CurrentUser,
) -> Any:
    """
    Read a Notion page by URL and return its content as markdown.
    
    This endpoint extracts the page ID from the provided Notion URL,
    fetches the page content from the Notion API, and returns it
    formatted as markdown along with page properties.
    
    **Authentication Required**: Yes
    
    **Example Request**:
    ```json
    {
        "page_url": "https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef"
    }
    ```
    
    **Example Response**:
    ```json
    {
        "page_id": "12345678-90ab-cdef-1234-567890abcdef",
        "title": "Your Page Title",
        "content": "# Your Page Title\\n\\nThis is the page content...",
        "url": "https://www.notion.so/your-workspace/Your-Page-Title-1234567890abcdef1234567890abcdef",
        "properties": {
            "Status": "In Progress",
            "Priority": "High"
        }
    }
    ```
    """
    try:
        page_content = await notion_service.get_page(str(request.page_url))
        
        return NotionPageResponse(
            page_id=page_content.page_id,
            title=page_content.title,
            content=page_content.content,
            url=page_content.url,
            properties=page_content.properties
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Notion URL: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Notion page: {str(e)}"
        )


@router.post("/debug-raw-api")
async def debug_raw_notion_api(
    request: NotionPageRequest,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """
    Debug endpoint to test raw Notion API calls and see the actual response.
    
    This endpoint makes the actual Notion API calls and returns the raw response
    so we can see exactly what Notion is returning.
    """
    print(f"\n🔍 DEBUG RAW API - Testing with URL: {request.page_url}")
    
    try:
        page_id = notion_service.extract_page_id_from_url(str(request.page_url))
        if not page_id:
            return {
                "error": "Could not extract page ID from URL",
                "input_url": str(request.page_url)
            }
        
        print(f"🔍 DEBUG RAW API - Extracted page ID: {page_id}")
        
        # Make raw API call using the HTTP client
        from app.core.config import settings
        from app.utils.http_client import http_client
        
        headers = {
            "Authorization": f"Bearer {settings.NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        response = await http_client.get(
            url=f"https://api.notion.com/v1/pages/{page_id}",
            headers=headers
        )
        
        return {
            "page_id": page_id,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_text": response.text,
            "success": response.status_code == 200
        }
            
    except Exception as e:
        print(f"❌ DEBUG RAW API - Error: {e}")
        return {
            "error": str(e),
            "input_url": str(request.page_url)
        }


@router.post("/debug-extract")
async def debug_extract_page_id(
    request: NotionPageRequest,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """
    Debug endpoint to test URL extraction with detailed logging.
    
    This endpoint only tests the URL extraction logic without making
    any Notion API calls, so it's safe to use for debugging.
    """
    print(f"\n🔍 DEBUG EXTRACT - Testing URL: {request.page_url}")
    
    page_id = notion_service.extract_page_id_from_url(str(request.page_url))
    
    result = {
        "input_url": str(request.page_url),
        "extracted_page_id": page_id,
        "success": page_id is not None
    }
    
    print(f"🔍 DEBUG EXTRACT - Result: {result}")
    
    return result


@router.get("/extract-page-id")
async def extract_page_id(
    page_url: str,
    current_user: CurrentUser,
) -> dict[str, str]:
    """
    Extract the page ID from a Notion URL without fetching the page content.
    
    This is a utility endpoint to help validate Notion URLs and extract
    page IDs for debugging purposes.
    
    **Authentication Required**: Yes
    
    **Parameters**:
    - `page_url` (query): The Notion page URL
    
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
    """
    page_id = notion_service.extract_page_id_from_url(page_url)
    
    if not page_id:
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract page ID from URL: {page_url}"
        )
    
    return {
        "page_id": page_id,
        "url": page_url
    }


@router.post("/ingest-book")
async def ingest_book(
    request: NotionPageRequest,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """
    Ingest a complete book from Notion with all chapters and pages.
    
    This endpoint takes a Notion book URL and:
    1. Parses the book page
    2. Finds all databases on the book page
    3. Identifies the chapters database
    4. Fetches all chapters from the database
    5. Fetches all pages from each chapter
    6. Returns a comprehensive book structure
    
    **Authentication Required**: Yes
    
    **Example Request**:
    ```json
    {
        "page_url": "https://www.notion.so/your-workspace/Your-Book-Title-1234567890abcdef1234567890abcdef"
    }
    ```
    
    **Response**:
    ```json
    {
        "status": "success",
        "message": "Book ingestion completed successfully",
        "book": {
            "id": "book-id",
            "title": "Book Title",
            "url": "book-url",
            "properties": {}
        },
        "summary": {
            "total_chapters": 5,
            "total_pages": 25,
            "databases_found": 2
        },
        "chapters": {
            "database_id": "chapters-db-id",
            "database_title": "Chapters",
            "chapters": [...]
        }
    }
    ```
    """
    try:
        from app.core.parsers import book_parser
        
        print(f"\n📚 BOOK INGESTION STARTED")
        print(f"📝 Book URL: {request.page_url}")
        print("="*80)
        
        # Ingest the complete book
        result = await book_parser.ingest_book(str(request.page_url))
        
        print(f"\n✅ BOOK INGESTION COMPLETED")
        print(f"📖 Book: {result.book_title}")
        print(f"📚 Chapters: {result.total_chapters}")
        print(f"📄 Total Pages: {result.total_pages}")
        print("="*80)
        
        # Prepare response data
        response_data = {
            "status": "success",
            "message": "Book ingestion completed successfully",
            "book": {
                "id": result.book_id,
                "title": result.book_title,
                "url": result.book_url,
                "properties": result.book_properties
            },
            "summary": {
                "total_chapters": result.total_chapters,
                "total_pages": result.total_pages,
                "databases_found": len(result.other_databases) + (1 if result.chapters_database else 0)
            }
        }
        
        # Add chapters data if available
        if result.chapters_database:
            response_data["chapters"] = {
                "database_id": result.chapters_database.id,
                "database_title": result.chapters_database.title,
                "chapters": [
                    {
                        "id": page.id,
                        "title": page.title,
                        "url": page.url,
                        "properties": page.properties,
                        "content_preview": page.content[:200] + "..." if len(page.content) > 200 else page.content
                    }
                    for page in result.chapters_database.pages
                ]
            }
        
        # Add other databases data
        if result.other_databases:
            response_data["other_databases"] = [
                {
                    "id": db.id,
                    "title": db.title,
                    "page_count": len(db.pages)
                }
                for db in result.other_databases
            ]
        
        return response_data
        
    except ValueError as e:
        print(f"\n❌ ERROR: Invalid Notion URL: {str(e)}")
        print("="*80 + "\n")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Notion URL: {str(e)}"
        )
    except Exception as e:
        print(f"\n❌ ERROR: Failed to ingest book: {str(e)}")
        print("="*80 + "\n")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest book: {str(e)}"
        )


@router.get("/mock-response")
async def mock_notion_response(current_user: CurrentUser) -> dict[str, Any]:
    """
    Mock endpoint that shows what a successful Notion API response looks like.
    
    This helps you understand the structure of the data we'll be parsing.
    """
    mock_page_data = {
        "object": "page",
        "id": "16b9e94d-1c93-81ce-a6c4-e74c508efea6",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"},
        "cover": None,
        "icon": None,
        "parent": {"type": "page_id", "page_id": "parent-page-id"},
        "archived": False,
        "properties": {
            "title": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "Book 1 - Jack", "link": None},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                        },
                        "plain_text": "Book 1 - Jack",
                        "href": None
                    }
                ]
            },
            "Status": {
                "id": "status",
                "type": "select",
                "select": {"id": "status-id", "name": "In Progress", "color": "blue"}
            },
            "Priority": {
                "id": "priority", 
                "type": "select",
                "select": {"id": "priority-id", "name": "High", "color": "red"}
            }
        },
        "url": "https://www.notion.so/Book-1-Jack-16b9e94d1c9381cea6c4e74c508efea6"
    }
    
    mock_blocks_data = {
        "object": "list",
        "results": [
            {
                "object": "block",
                "id": "block-1",
                "parent": {"type": "page_id", "page_id": "16b9e94d-1c93-81ce-a6c4-e74c508efea6"},
                "created_time": "2023-01-01T00:00:00.000Z",
                "last_edited_time": "2023-01-01T00:00:00.000Z",
                "created_by": {"object": "user", "id": "user-id"},
                "last_edited_by": {"object": "user", "id": "user-id"},
                "has_children": False,
                "archived": False,
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "This is the first paragraph of the page content."},
                            "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"},
                            "plain_text": "This is the first paragraph of the page content.",
                            "href": None
                        }
                    ],
                    "color": "default"
                }
            },
            {
                "object": "block",
                "id": "block-2",
                "parent": {"type": "page_id", "page_id": "16b9e94d-1c93-81ce-a6c4-e74c508efea6"},
                "created_time": "2023-01-01T00:00:00.000Z",
                "last_edited_time": "2023-01-01T00:00:00.000Z",
                "created_by": {"object": "user", "id": "user-id"},
                "last_edited_by": {"object": "user", "id": "user-id"},
                "has_children": False,
                "archived": False,
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Chapter 1"},
                            "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"},
                            "plain_text": "Chapter 1",
                            "href": None
                        }
                    ],
                    "is_toggleable": False,
                    "color": "default"
                }
            },
            {
                "object": "block",
                "id": "block-3",
                "parent": {"type": "page_id", "page_id": "16b9e94d-1c93-81ce-a6c4-e74c508efea6"},
                "created_time": "2023-01-01T00:00:00.000Z",
                "last_edited_time": "2023-01-01T00:00:00.000Z",
                "created_by": {"object": "user", "id": "user-id"},
                "last_edited_by": {"object": "user", "id": "user-id"},
                "has_children": False,
                "archived": False,
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "First bullet point"},
                            "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"},
                            "plain_text": "First bullet point",
                            "href": None
                        }
                    ],
                    "color": "default"
                }
            }
        ],
        "next_cursor": None,
        "has_more": False,
        "type": "block",
        "block": {}
    }
    
    return {
        "message": "This is what a successful Notion API response looks like",
        "page_data": mock_page_data,
        "blocks_data": mock_blocks_data,
        "parsed_content": {
            "title": "Book 1 - Jack",
            "properties": {
                "Status": "In Progress",
                "Priority": "High"
            },
            "markdown_content": "This is the first paragraph of the page content.\n\n## Chapter 1\n\n- First bullet point"
        }
    }


@router.get("/test-http-client")
async def test_http_client(current_user: CurrentUser) -> dict[str, Any]:
    """
    Test endpoint to demonstrate the HTTP client with comprehensive logging.
    
    This makes a simple request to httpbin.org to show the logging in action.
    """
    from app.utils.http_client import http_client
    
    try:
        # Make a test request to httpbin.org
        response = await http_client.get(
            url="https://httpbin.org/json",
            headers={"User-Agent": "Beanstalk-Notion-Service/1.0"}
        )
        
        return {
            "message": "HTTP client test completed successfully",
            "status_code": response.status_code,
            "response_data": response.json(),
            "note": "Check the terminal logs above to see the detailed request/response logging"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "HTTP client test failed - check terminal logs for details"
        }


@router.get("/health")
async def notion_health_check(current_user: CurrentUser) -> dict[str, str]:
    """
    Check if the Notion API is properly configured.
    
    This endpoint verifies that the Notion API key is set and
    the service is ready to make requests.
    
    **Authentication Required**: Yes
    
    **Response**:
    ```json
    {
        "status": "healthy",
        "message": "Notion service is properly configured"
    }
    ```
    """
    from app.core.config import settings
    
    if settings.NOTION_API_KEY == "changethis":
        raise HTTPException(
            status_code=503,
            detail="Notion API key not configured. Please set NOTION_API_KEY in your environment."
        )
    
    return {
        "status": "healthy",
        "message": "Notion service is properly configured"
    }
