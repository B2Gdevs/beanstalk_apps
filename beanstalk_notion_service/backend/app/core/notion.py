"""
Notion API service for reading pages and content.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from app.core.config import settings
from app.utils.http_client import http_client


class NotionPageContent(BaseModel):
    """Model for Notion page content."""
    
    page_id: str = Field(..., description="The Notion page ID")
    title: str = Field(..., description="The page title")
    content: str = Field(..., description="The page content as markdown")
    url: str = Field(..., description="The original Notion page URL")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Page properties")


class NotionService:
    """Service for interacting with Notion API."""
    
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def extract_page_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract Notion page ID from a Notion URL.
        
        Args:
            url: Notion page URL
            
        Returns:
            Page ID if found, None otherwise
        """
        print(f"\n🔍 DEBUG: Extracting page ID from URL: {url}")
        
        # Handle different Notion URL formats
        patterns = [
            # Standard formats with 32-char hex ID
            r"notion\.so/([a-f0-9]{32})",  # notion.so/32-char-id
            r"notion\.site/([a-f0-9]{32})",  # notion.site/32-char-id
            r"www\.notion\.so/([a-f0-9]{32})",  # www.notion.so/32-char-id
            
            # UUID formats
            r"notion\.so/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",  # notion.so/uuid
            r"notion\.site/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",  # notion.site/uuid
            r"www\.notion\.so/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",  # www.notion.so/uuid
            
            # Page title formats (like your URL: Book-1-Jack-16b9e94d1c9381cea6c4e74c508efea6)
            r"notion\.so/[^/]+-([a-f0-9]{32})",  # notion.so/Page-Title-32-char-id
            r"notion\.site/[^/]+-([a-f0-9]{32})",  # notion.site/Page-Title-32-char-id
            r"www\.notion\.so/[^/]+-([a-f0-9]{32})",  # www.notion.so/Page-Title-32-char-id
            
            # Workspace + page title formats
            r"notion\.so/[^/]+/[^/]+-([a-f0-9]{32})",  # notion.so/workspace/Page-Title-32-char-id
            r"notion\.site/[^/]+/[^/]+-([a-f0-9]{32})",  # notion.site/workspace/Page-Title-32-char-id
            r"www\.notion\.so/[^/]+/[^/]+-([a-f0-9]{32})",  # www.notion.so/workspace/Page-Title-32-char-id
        ]
        
        print(f"🔍 DEBUG: Testing {len(patterns)} URL patterns...")
        
        for i, pattern in enumerate(patterns, 1):
            print(f"🔍 DEBUG: Pattern {i}: {pattern}")
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                page_id = match.group(1)
                print(f"✅ DEBUG: Found match! Raw page ID: {page_id}")
                
                # Convert to proper UUID format if needed
                if len(page_id) == 32:
                    page_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
                    print(f"✅ DEBUG: Converted to UUID format: {page_id}")
                
                return page_id
            else:
                print(f"❌ DEBUG: No match for pattern {i}")
        
        print(f"❌ DEBUG: No patterns matched for URL: {url}")
        return None
    
    async def get_page(self, page_url: str) -> NotionPageContent:
        """
        Retrieve a Notion page by URL.
        
        Args:
            page_url: The Notion page URL
            
        Returns:
            NotionPageContent object with page data
            
        Raises:
            ValueError: If page ID cannot be extracted from URL
            httpx.HTTPError: If API request fails
        """
        page_id = self.extract_page_id_from_url(page_url)
        if not page_id:
            raise ValueError(f"Could not extract page ID from URL: {page_url}")
        
        # Get page properties using the HTTP client
        page_response = await http_client.get(
            url=f"{self.base_url}/pages/{page_id}",
            headers=self.headers
        )
        page_data = page_response.json()
        
        # Get page content (blocks) using the HTTP client
        blocks_response = await http_client.get(
            url=f"{self.base_url}/blocks/{page_id}/children",
            headers=self.headers
        )
        blocks_data = blocks_response.json()
        
        # Extract title from page properties
        title = self._extract_title(page_data)
        
        # Convert blocks to markdown content
        content = self._blocks_to_markdown(blocks_data.get("results", []))
        
        # Extract properties
        properties = self._extract_properties(page_data)
        
        return NotionPageContent(
            page_id=page_id,
            title=title,
            content=content,
            url=page_url,
            properties=properties
        )
    
    def _extract_title(self, page_data: Dict[str, Any]) -> str:
        """Extract title from page data."""
        properties = page_data.get("properties", {})
        
        # Try different title property names
        title_properties = ["title", "Name", "Page", "Title"]
        
        for prop_name in title_properties:
            if prop_name in properties:
                prop = properties[prop_name]
                if prop.get("type") == "title" and prop.get("title"):
                    return prop["title"][0]["text"]["content"]
        
        # Fallback to page ID if no title found
        return f"Untitled Page ({page_data.get('id', 'Unknown')[:8]})"
    
    def _extract_properties(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and format page properties."""
        properties = page_data.get("properties", {})
        formatted_properties = {}
        
        for key, value in properties.items():
            prop_type = value.get("type")
            
            if prop_type == "title" and value.get("title"):
                formatted_properties[key] = value["title"][0]["text"]["content"]
            elif prop_type == "rich_text" and value.get("rich_text"):
                formatted_properties[key] = "".join([text["text"]["content"] for text in value["rich_text"]])
            elif prop_type == "select" and value.get("select"):
                formatted_properties[key] = value["select"]["name"]
            elif prop_type == "multi_select" and value.get("multi_select"):
                formatted_properties[key] = [item["name"] for item in value["multi_select"]]
            elif prop_type == "date" and value.get("date"):
                formatted_properties[key] = value["date"]["start"]
            elif prop_type == "checkbox" and "checkbox" in value:
                formatted_properties[key] = value["checkbox"]
            elif prop_type == "number" and "number" in value:
                formatted_properties[key] = value["number"]
            else:
                formatted_properties[key] = str(value)
        
        return formatted_properties
    
    def _blocks_to_markdown(self, blocks: List[Dict[str, Any]]) -> str:
        """Convert Notion blocks to markdown content."""
        markdown_lines = []
        
        for block in blocks:
            block_type = block.get("type")
            
            if block_type == "paragraph":
                text = self._extract_text_from_block(block)
                if text:
                    markdown_lines.append(text)
            elif block_type == "heading_1":
                text = self._extract_text_from_block(block)
                if text:
                    markdown_lines.append(f"# {text}")
            elif block_type == "heading_2":
                text = self._extract_text_from_block(block)
                if text:
                    markdown_lines.append(f"## {text}")
            elif block_type == "heading_3":
                text = self._extract_text_from_block(block)
                if text:
                    markdown_lines.append(f"### {text}")
            elif block_type == "bulleted_list_item":
                text = self._extract_text_from_block(block)
                if text:
                    markdown_lines.append(f"- {text}")
            elif block_type == "numbered_list_item":
                text = self._extract_text_from_block(block)
                if text:
                    markdown_lines.append(f"1. {text}")
            elif block_type == "code":
                text = self._extract_text_from_block(block)
                language = block.get("code", {}).get("language", "")
                if text:
                    markdown_lines.append(f"```{language}")
                    markdown_lines.append(text)
                    markdown_lines.append("```")
            elif block_type == "quote":
                text = self._extract_text_from_block(block)
                if text:
                    markdown_lines.append(f"> {text}")
            elif block_type == "divider":
                markdown_lines.append("---")
            elif block_type == "to_do":
                text = self._extract_text_from_block(block)
                checked = block.get("to_do", {}).get("checked", False)
                checkbox = "- [x]" if checked else "- [ ]"
                if text:
                    markdown_lines.append(f"{checkbox} {text}")
        
        return "\n".join(markdown_lines)
    
    def _extract_text_from_block(self, block: Dict[str, Any]) -> str:
        """Extract plain text from a Notion block."""
        block_type = block.get("type")
        block_data = block.get(block_type, {})
        
        if "rich_text" in block_data:
            return "".join([text["text"]["content"] for text in block_data["rich_text"]])
        
        return ""


# Global instance
notion_service = NotionService()
