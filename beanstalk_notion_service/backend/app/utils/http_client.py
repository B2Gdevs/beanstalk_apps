"""
HTTP Client utility for making requests to third-party APIs with comprehensive logging.

This module provides a standardized way to make HTTP requests with detailed logging
for debugging, monitoring, and troubleshooting external API integrations.
"""

import json
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel


class RequestLog(BaseModel):
    """Model for logging HTTP request details."""
    
    method: str
    url: str
    headers: Dict[str, str]
    params: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = None
    timestamp: str


class ResponseLog(BaseModel):
    """Model for logging HTTP response details."""
    
    status_code: int
    headers: Dict[str, str]
    content: str
    json_data: Optional[Dict[str, Any]] = None
    response_time_ms: float
    timestamp: str


class HTTPClientError(Exception):
    """Custom exception for HTTP client errors."""
    
    def __init__(self, message: str, request_log: RequestLog, response_log: Optional[ResponseLog] = None):
        self.message = message
        self.request_log = request_log
        self.response_log = response_log
        super().__init__(self.message)


class HTTPClient:
    """
    HTTP client with comprehensive logging for third-party API requests.
    
    Features:
    - Detailed request/response logging
    - Automatic JSON parsing
    - Error handling with context
    - Performance timing
    - Configurable timeouts
    - Support for various HTTP methods
    """
    
    def __init__(self, default_timeout: float = 30.0, default_headers: Optional[Dict[str, str]] = None):
        """
        Initialize the HTTP client.
        
        Args:
            default_timeout: Default timeout for requests in seconds
            default_headers: Default headers to include in all requests
        """
        self.default_timeout = default_timeout
        self.default_headers = default_headers or {}
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize headers for logging (remove sensitive data)."""
        sanitized = headers.copy()
        
        # Remove or mask sensitive headers
        sensitive_headers = ['authorization', 'x-api-key', 'cookie', 'set-cookie']
        for header in sensitive_headers:
            if header in sanitized:
                sanitized[header] = f"***{sanitized[header][-4:]}" if len(sanitized[header]) > 4 else "***"
            if header.upper() in sanitized:
                sanitized[header.upper()] = f"***{sanitized[header.upper()][-4:]}" if len(sanitized[header.upper()]) > 4 else "***"
        
        return sanitized
    
    def _log_request(self, request_log: RequestLog) -> None:
        """Log outgoing request details."""
        print("\n" + "="*100)
        print("🌐 OUTGOING HTTP REQUEST")
        print("="*100)
        print(f"⏰ Timestamp: {request_log.timestamp}")
        print(f"🔗 Method: {request_log.method}")
        print(f"📍 URL: {request_log.url}")
        print(f"⏱️  Timeout: {request_log.timeout}s")
        
        if request_log.headers:
            print(f"\n📋 Headers:")
            sanitized_headers = self._sanitize_headers(request_log.headers)
            for key, value in sanitized_headers.items():
                print(f"   {key}: {value}")
        
        if request_log.params:
            print(f"\n🔍 Query Parameters:")
            for key, value in request_log.params.items():
                print(f"   {key}: {value}")
        
        if request_log.json_data:
            print(f"\n📦 JSON Payload:")
            try:
                formatted_json = json.dumps(request_log.json_data, indent=2)
                print(formatted_json)
            except Exception as e:
                print(f"   Error formatting JSON: {e}")
                print(f"   Raw data: {request_log.json_data}")
        
        if request_log.form_data:
            print(f"\n📝 Form Data:")
            for key, value in request_log.form_data.items():
                print(f"   {key}: {value}")
        
        print("="*100)
    
    def _log_response(self, response_log: ResponseLog, request_log: RequestLog) -> None:
        """Log incoming response details."""
        print("\n" + "="*100)
        print("📥 INCOMING HTTP RESPONSE")
        print("="*100)
        print(f"⏰ Timestamp: {response_log.timestamp}")
        print(f"📊 Status Code: {response_log.status_code}")
        print(f"⏱️  Response Time: {response_log.response_time_ms:.2f}ms")
        
        if response_log.headers:
            print(f"\n📋 Response Headers:")
            for key, value in response_log.headers.items():
                print(f"   {key}: {value}")
        
        if response_log.json_data:
            print(f"\n📦 JSON Response:")
            try:
                formatted_json = json.dumps(response_log.json_data, indent=2)
                print(formatted_json)
            except Exception as e:
                print(f"   Error formatting JSON: {e}")
                print(f"   Raw data: {response_log.json_data}")
        else:
            print(f"\n📄 Raw Response Content:")
            content_preview = response_log.content[:500] + "..." if len(response_log.content) > 500 else response_log.content
            print(content_preview)
        
        print("="*100)
    
    def _log_error(self, error: Exception, request_log: RequestLog, response_log: Optional[ResponseLog] = None) -> None:
        """Log error details."""
        print("\n" + "="*100)
        print("❌ HTTP REQUEST ERROR")
        print("="*100)
        print(f"⏰ Timestamp: {request_log.timestamp}")
        print(f"🔗 Method: {request_log.method}")
        print(f"📍 URL: {request_log.url}")
        print(f"💥 Error Type: {type(error).__name__}")
        print(f"💥 Error Message: {str(error)}")
        
        if response_log:
            print(f"📊 Response Status: {response_log.status_code}")
            print(f"⏱️  Response Time: {response_log.response_time_ms:.2f}ms")
            if response_log.content:
                content_preview = response_log.content[:500] + "..." if len(response_log.content) > 500 else response_log.content
                print(f"📄 Response Content: {content_preview}")
        
        print("="*100)
    
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        raise_for_status: bool = True
    ) -> httpx.Response:
        """
        Make an HTTP request with comprehensive logging.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            headers: Request headers
            params: Query parameters
            json_data: JSON payload
            form_data: Form data payload
            timeout: Request timeout in seconds
            raise_for_status: Whether to raise exception for HTTP error status codes
            
        Returns:
            httpx.Response object
            
        Raises:
            HTTPClientError: If the request fails
        """
        # Merge default headers with request headers
        merged_headers = {**self.default_headers, **(headers or {})}
        request_timeout = timeout or self.default_timeout
        start_time = time.time()
        
        # Create request log
        request_log = RequestLog(
            method=method.upper(),
            url=url,
            headers=merged_headers,
            params=params,
            json_data=json_data,
            form_data=form_data,
            timeout=request_timeout,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        )
        
        # Log the outgoing request
        self._log_request(request_log)
        
        response_log = None
        
        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                # Make the request
                response = await client.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    params=params,
                    json=json_data,
                    data=form_data
                )
                
                # Calculate response time
                response_time_ms = (time.time() - start_time) * 1000
                
                # Parse response content
                try:
                    json_data = response.json()
                except (json.JSONDecodeError, ValueError):
                    json_data = None
                
                # Create response log
                response_log = ResponseLog(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    content=response.text,
                    json_data=json_data,
                    response_time_ms=response_time_ms,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                )
                
                # Log the incoming response
                self._log_response(response_log, request_log)
                
                # Raise for status if requested
                if raise_for_status:
                    response.raise_for_status()
                
                return response
                
        except httpx.HTTPStatusError as e:
            # Calculate response time for error case
            response_time_ms = (time.time() - start_time) * 1000
            
            # Create error response log
            response_log = ResponseLog(
                status_code=e.response.status_code,
                headers=dict(e.response.headers),
                content=e.response.text,
                json_data=None,
                response_time_ms=response_time_ms,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
            
            # Log the error
            self._log_error(e, request_log, response_log)
            
            raise HTTPClientError(
                f"HTTP {e.response.status_code} error: {e.response.text}",
                request_log,
                response_log
            )
            
        except httpx.TimeoutException as e:
            response_time_ms = (time.time() - start_time) * 1000
            self._log_error(e, request_log)
            raise HTTPClientError(f"Request timeout after {request_timeout}s", request_log)
            
        except httpx.RequestError as e:
            response_time_ms = (time.time() - start_time) * 1000
            self._log_error(e, request_log)
            raise HTTPClientError(f"Request error: {str(e)}", request_log)
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            self._log_error(e, request_log)
            raise HTTPClientError(f"Unexpected error: {str(e)}", request_log)
    
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        raise_for_status: bool = True
    ) -> httpx.Response:
        """Make a GET request."""
        return await self.request(
            method="GET",
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
            raise_for_status=raise_for_status
        )
    
    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        raise_for_status: bool = True
    ) -> httpx.Response:
        """Make a POST request."""
        return await self.request(
            method="POST",
            url=url,
            headers=headers,
            params=params,
            json_data=json_data,
            form_data=form_data,
            timeout=timeout,
            raise_for_status=raise_for_status
        )
    
    async def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        raise_for_status: bool = True
    ) -> httpx.Response:
        """Make a PUT request."""
        return await self.request(
            method="PUT",
            url=url,
            headers=headers,
            params=params,
            json_data=json_data,
            form_data=form_data,
            timeout=timeout,
            raise_for_status=raise_for_status
        )
    
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        raise_for_status: bool = True
    ) -> httpx.Response:
        """Make a DELETE request."""
        return await self.request(
            method="DELETE",
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
            raise_for_status=raise_for_status
        )


# Global instance for easy importing
http_client = HTTPClient()
