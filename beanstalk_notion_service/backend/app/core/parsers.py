"""
Notion parsers for different content types.

This module provides specialized parsers for different types of Notion content:
- BookParser: Handles book-level parsing and database discovery
- ChapterParser: Handles chapter database parsing
- PageParser: Handles individual page content parsing
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from app.core.config import settings
from app.utils.http_client import http_client


class NotionBlock(BaseModel):
    """Model for a Notion block."""
    
    id: str
    type: str
    content: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    children: List['NotionBlock'] = Field(default_factory=list)


class NotionPage(BaseModel):
    """Model for a Notion page."""
    
    id: str
    title: str
    url: str
    content: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    blocks: List[NotionBlock] = Field(default_factory=list)


class NotionDatabase(BaseModel):
    """Model for a Notion database."""
    
    id: str
    title: str
    pages: List[NotionPage] = Field(default_factory=list)


class BookIngestionResult(BaseModel):
    """Model for the complete book ingestion result."""
    
    book_id: str
    book_title: str
    book_url: str
    book_properties: Dict[str, Any] = Field(default_factory=dict)
    chapters_database: Optional[NotionDatabase] = None
    other_databases: List[NotionDatabase] = Field(default_factory=list)
    total_chapters: int = 0
    total_pages: int = 0


class BaseParser:
    """Base class for all Notion parsers."""
    
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def _extract_text_from_block(self, block: Dict[str, Any]) -> str:
        """Extract plain text from a Notion block."""
        block_type = block.get("type", "")
        
        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            return "".join([text.get("plain_text", "") for text in rich_text])
        
        elif block_type == "bulleted_list_item":
            rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
            text = "".join([text.get("plain_text", "") for text in rich_text])
            return f"- {text}"
        
        elif block_type == "numbered_list_item":
            rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
            text = "".join([text.get("plain_text", "") for text in rich_text])
            return f"1. {text}"
        
        elif block_type == "to_do":
            rich_text = block.get("to_do", {}).get("rich_text", [])
            text = "".join([text.get("plain_text", "") for text in rich_text])
            checked = block.get("to_do", {}).get("checked", False)
            checkbox = "☑" if checked else "☐"
            return f"{checkbox} {text}"
        
        elif block_type == "code":
            rich_text = block.get("code", {}).get("rich_text", [])
            text = "".join([text.get("plain_text", "") for text in rich_text])
            language = block.get("code", {}).get("language", "")
            return f"```{language}\n{text}\n```"
        
        elif block_type == "quote":
            rich_text = block.get("quote", {}).get("rich_text", [])
            text = "".join([text.get("plain_text", "") for text in rich_text])
            return f"> {text}"
        
        elif block_type == "callout":
            rich_text = block.get("callout", {}).get("rich_text", [])
            text = "".join([text.get("plain_text", "") for text in rich_text])
            icon = block.get("callout", {}).get("icon", {}).get("emoji", "💡")
            return f"{icon} {text}"
        
        return ""
    
    def _blocks_to_markdown(self, blocks: List[Dict[str, Any]]) -> str:
        """Convert Notion blocks to markdown content."""
        markdown_lines = []
        
        for block in blocks:
            block_type = block.get("type", "")
            text = self._extract_text_from_block(block)
            
            if text:
                if block_type == "heading_1":
                    markdown_lines.append(f"# {text}")
                elif block_type == "heading_2":
                    markdown_lines.append(f"## {text}")
                elif block_type == "heading_3":
                    markdown_lines.append(f"### {text}")
                else:
                    markdown_lines.append(text)
                
                markdown_lines.append("")  # Add blank line after each block
        
        return "\n".join(markdown_lines)
    
    def _extract_title_from_page(self, page_data: Dict[str, Any]) -> str:
        """Extract title from page data."""
        properties = page_data.get("properties", {})
        
        # Look for title property
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_array = prop_data.get("title", [])
                if title_array:
                    return title_array[0].get("plain_text", "Untitled")
        
        # Fallback to first property that has a name
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") in ["rich_text", "text"]:
                rich_text = prop_data.get("rich_text", [])
                if rich_text:
                    return rich_text[0].get("plain_text", "Untitled")
        
        return "Untitled"
    
    def _extract_properties_from_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract properties from page data."""
        properties = page_data.get("properties", {})
        extracted = {}
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            
            if prop_type == "title":
                title_array = prop_data.get("title", [])
                extracted[prop_name] = title_array[0].get("plain_text", "") if title_array else ""
            
            elif prop_type == "rich_text":
                rich_text = prop_data.get("rich_text", [])
                extracted[prop_name] = "".join([text.get("plain_text", "") for text in rich_text])
            
            elif prop_type == "select":
                select_data = prop_data.get("select")
                extracted[prop_name] = select_data.get("name", "") if select_data else ""
            
            elif prop_type == "multi_select":
                multi_select = prop_data.get("multi_select", [])
                extracted[prop_name] = [item.get("name", "") for item in multi_select]
            
            elif prop_type == "date":
                date_data = prop_data.get("date")
                extracted[prop_name] = date_data.get("start", "") if date_data else ""
            
            elif prop_type == "number":
                extracted[prop_name] = prop_data.get("number")
            
            elif prop_type == "checkbox":
                extracted[prop_name] = prop_data.get("checkbox", False)
            
            elif prop_type == "url":
                extracted[prop_name] = prop_data.get("url", "")
            
            elif prop_type == "email":
                extracted[prop_name] = prop_data.get("email", "")
            
            elif prop_type == "phone_number":
                extracted[prop_name] = prop_data.get("phone_number", "")
        
        return extracted


class PageParser(BaseParser):
    """Parser for individual Notion pages."""
    
    async def parse_page(self, page_id: str, page_url: str) -> NotionPage:
        """Parse a single Notion page."""
        print(f"🔍 Parsing page: {page_id}")
        
        # Get page properties
        page_response = await http_client.get(
            url=f"{self.base_url}/pages/{page_id}",
            headers=self.headers
        )
        page_data = page_response.json()
        
        # Get page content (blocks)
        blocks_response = await http_client.get(
            url=f"{self.base_url}/blocks/{page_id}/children",
            headers=self.headers
        )
        blocks_data = blocks_response.json()
        
        # Extract data
        title = self._extract_title_from_page(page_data)
        properties = self._extract_properties_from_page(page_data)
        content = self._blocks_to_markdown(blocks_data.get("results", []))
        
        # Convert blocks to NotionBlock objects
        blocks = []
        for block_data in blocks_data.get("results", []):
            block = NotionBlock(
                id=block_data.get("id", ""),
                type=block_data.get("type", ""),
                content=self._extract_text_from_block(block_data),
                properties={}
            )
            blocks.append(block)
        
        return NotionPage(
            id=page_id,
            title=title,
            url=page_url,
            content=content,
            properties=properties,
            blocks=blocks
        )


class ChapterParser(BaseParser):
    """Parser for chapter databases."""
    
    async def parse_database(self, database_id: str) -> NotionDatabase:
        """Parse a chapter database and all its pages."""
        print(f"🔍 Parsing database: {database_id}")
        
        # Get database info
        db_response = await http_client.get(
            url=f"{self.base_url}/databases/{database_id}",
            headers=self.headers
        )
        db_data = db_response.json()
        
        # Get database title
        title = db_data.get("title", [{}])[0].get("plain_text", "Untitled Database")
        
        # Query all pages in the database
        query_response = await http_client.post(
            url=f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json_data={}
        )
        query_data = query_response.json()
        
        # Parse each page
        pages = []
        page_parser = PageParser()
        
        for page_data in query_data.get("results", []):
            page_id = page_data.get("id", "")
            page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
            
            try:
                page = await page_parser.parse_page(page_id, page_url)
                pages.append(page)
                print(f"  ✅ Parsed page: {page.title}")
            except Exception as e:
                print(f"  ❌ Failed to parse page {page_id}: {e}")
        
        return NotionDatabase(
            id=database_id,
            title=title,
            pages=pages
        )


class BookParser(BaseParser):
    """Parser for book-level content and database discovery."""
    
    def __init__(self):
        super().__init__()
        self.chapter_parser = ChapterParser()
        self.page_parser = PageParser()
    
    def extract_page_id_from_url(self, url: str) -> Optional[str]:
        """Extract Notion page ID from a Notion URL."""
        print(f"🔍 Extracting page ID from URL: {url}")
        
        patterns = [
            r"notion\.so/([a-f0-9]{32})",
            r"notion\.site/([a-f0-9]{32})",
            r"www\.notion\.so/([a-f0-9]{32})",
            r"notion\.so/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
            r"notion\.site/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
            r"www\.notion\.so/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
            r"notion\.so/[^/]+-([a-f0-9]{32})",
            r"notion\.site/[^/]+-([a-f0-9]{32})",
            r"www\.notion\.so/[^/]+-([a-f0-9]{32})",
            r"notion\.so/[^/]+/[^/]+-([a-f0-9]{32})",
            r"notion\.site/[^/]+/[^/]+-([a-f0-9]{32})",
            r"www\.notion\.so/[^/]+/[^/]+-([a-f0-9]{32})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                page_id = match.group(1)
                if len(page_id) == 32:
                    page_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
                print(f"✅ Extracted page ID: {page_id}")
                return page_id
        
        print(f"❌ Could not extract page ID from URL: {url}")
        return None
    
    async def ingest_book(self, book_url: str) -> BookIngestionResult:
        """Ingest a complete book with all its chapters and pages."""
        print(f"\n📚 Starting book ingestion for: {book_url}")
        print("="*80)
        
        # Extract book page ID
        book_id = self.extract_page_id_from_url(book_url)
        if not book_id:
            raise ValueError(f"Could not extract page ID from URL: {book_url}")
        
        # Parse the book page
        book_page = await self.page_parser.parse_page(book_id, book_url)
        print(f"📖 Book: {book_page.title}")
        
        # Get book page blocks to find databases
        blocks_response = await http_client.get(
            url=f"{self.base_url}/blocks/{book_id}/children",
            headers=self.headers
        )
        blocks_data = blocks_response.json()
        
        # Find all databases on the book page
        databases = []
        chapters_database = None
        
        for block in blocks_data.get("results", []):
            if block.get("type") == "child_database":
                database_id = block.get("id", "")
                database_title = block.get("child_database", {}).get("title", "Untitled")
                
                print(f"🗄️  Found database: {database_title} ({database_id})")
                
                # Parse the database
                try:
                    database = await self.chapter_parser.parse_database(database_id)
                    databases.append(database)
                    
                    # Assume the first database is chapters (you can make this more sophisticated)
                    if chapters_database is None:
                        chapters_database = database
                        print(f"📚 Using as chapters database: {database.title}")
                    
                except Exception as e:
                    print(f"❌ Failed to parse database {database_id}: {e}")
        
        # Calculate totals
        total_chapters = len(chapters_database.pages) if chapters_database else 0
        total_pages = sum(len(db.pages) for db in databases)
        
        print(f"\n📊 Ingestion Summary:")
        print(f"  • Book: {book_page.title}")
        print(f"  • Chapters: {total_chapters}")
        print(f"  • Total Pages: {total_pages}")
        print(f"  • Databases Found: {len(databases)}")
        print("="*80)
        
        return BookIngestionResult(
            book_id=book_id,
            book_title=book_page.title,
            book_url=book_url,
            book_properties=book_page.properties,
            chapters_database=chapters_database,
            other_databases=[db for db in databases if db != chapters_database],
            total_chapters=total_chapters,
            total_pages=total_pages
        )


# Global instances
book_parser = BookParser()
chapter_parser = ChapterParser()
page_parser = PageParser()
