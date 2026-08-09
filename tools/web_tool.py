"""
Web Research Tool
Fetches and extracts information from web pages.
"""
import requests
from typing import Dict, Any, Optional
import logging

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logging.warning("BeautifulSoup4 not installed. Web scraping will be limited.")

from .base_tool import BaseTool
from config import ENABLE_WEB_RESEARCH

logger = logging.getLogger(__name__)


class WebTool(BaseTool):
    """
    Web research tool.
    Fetches and extracts information from websites.
    """
    
    def __init__(self):
        super().__init__(
            tool_id="web_tool",
            name="Web Tool",
            description="Fetch and extract information from web pages"
        )
        self.enabled = ENABLE_WEB_RESEARCH
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (AI Swarm Research Bot)"
        })
    
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute a web operation"""
        operations = {
            "fetch": self._fetch_page,
            "fetch_text": self._fetch_text,
            "search_docs": self._search_documentation,
            "get_status": self._get_status,
        }
        
        if operation not in operations:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}"
            }
        
        return operations[operation](**kwargs)
    
    def validate_params(self, operation: str = None, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters"""
        if not operation:
            return False, "Operation is required"
        
        if operation in ["fetch", "fetch_text", "get_status"]:
            url = kwargs.get("url")
            if not url:
                return False, "URL is required"
            
            # Basic URL validation
            if not url.startswith(("http://", "https://")):
                return False, "URL must start with http:// or https://"
        
        return True, None
    
    def _fetch_page(self, url: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
        """Fetch a web page"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            return {
                "status": "success",
                "url": url,
                "content": response.text,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "size": len(response.content)
            }
        
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": f"Request timed out after {timeout} seconds",
                "url": url
            }
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "error": f"HTTP error: {e}",
                "url": url
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }
    
    def _fetch_text(self, url: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
        """Fetch and extract clean text from a web page"""
        # Fetch the page
        result = self._fetch_page(url, timeout, **kwargs)
        
        if result["status"] != "success":
            return result
        
        # Extract text
        if not BS4_AVAILABLE:
            return {
                "status": "error",
                "error": "BeautifulSoup4 not available for text extraction"
            }
        
        try:
            soup = BeautifulSoup(result["content"], "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract title
            title = soup.title.string if soup.title else "No title"
            
            # Extract main content (try common patterns)
            main_content = None
            for tag in ["main", "article", "div.content", "div.main"]:
                element = soup.select_one(tag)
                if element:
                    main_content = element.get_text(strip=True, separator='\n')
                    break
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "text": text[:10000],  # Limit to 10k chars
                "main_content": main_content[:5000] if main_content else None,
                "word_count": len(text.split())
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to extract text: {e}",
                "url": url
            }
    
    def _search_documentation(
        self,
        library: str,
        query: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search for library documentation.
        This is a placeholder - would integrate with specific doc sites.
        """
        # Common documentation URL patterns
        doc_urls = {
            "python": f"https://docs.python.org/3/search.html?q={query}" if query else "https://docs.python.org/3/",
            "numpy": "https://numpy.org/doc/stable/",
            "pandas": "https://pandas.pydata.org/docs/",
            "requests": "https://requests.readthedocs.io/en/latest/",
            "django": "https://docs.djangoproject.com/en/stable/",
            "flask": "https://flask.palletsprojects.com/",
            "fastapi": "https://fastapi.tiangolo.com/",
        }
        
        library_lower = library.lower()
        
        if library_lower in doc_urls:
            url = doc_urls[library_lower]
            return self._fetch_text(url, **kwargs)
        else:
            return {
                "status": "error",
                "error": f"Documentation URL not configured for: {library}",
                "suggestion": f"Try searching: https://www.google.com/search?q={library}+documentation"
            }
    
    def _get_status(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        """Check if a URL is accessible"""
        try:
            response = self.session.head(url, timeout=timeout, allow_redirects=True)
            
            return {
                "status": "success",
                "url": url,
                "accessible": True,
                "status_code": response.status_code,
                "redirected": len(response.history) > 0,
                "final_url": response.url
            }
        
        except Exception as e:
            return {
                "status": "success",
                "url": url,
                "accessible": False,
                "error": str(e)
            }
    
    # Convenience methods
    
    def fetch_documentation(self, library: str) -> Dict[str, Any]:
        """Fetch documentation for a library"""
        return self.run(operation="search_docs", library=library)
    
    def check_url(self, url: str) -> bool:
        """Quick check if URL is accessible"""
        result = self.run(operation="get_status", url=url)
        return result.get("accessible", False)