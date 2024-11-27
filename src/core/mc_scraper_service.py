import logging
from typing import Dict, Any, Optional
from venv import logger
from src.core.scraping_service import ScrapingService
from src.transformers.crawl_transformers_main_content import CrawlTransformersMainContent
from src.transformers.crawl_transformers import CrawlTransformers
from src.config.llm_config import get_llm_config

logger = logging.getLogger(__name__)    

class MCScraperService:
    def __init__(self, link: str):
        """
        Initialize the MC (Main Content) Scraper Node.

        :param link (str): The URL to scrape.
        """
        self.link = link
        self.llm_config = get_llm_config()
        self.scraping_service = ScrapingService()
        self.crawl_transformers = CrawlTransformers()
        self.main_content_extractor = CrawlTransformersMainContent(self.llm_config)

    async def fetch_main_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the main content from a URL.

        :param url (str): The URL to scrape.

        :returns Optional[Dict[str, Any]]: The main content data or None if fetching fails.
        """
        try:
            # Fetch the HTML content
            fetched_data = await self.scraping_service.fetch_url(url, render_js=True)

            # Check if fetch was successful
            if not fetched_data.html or fetched_data.status_code != 200:
                return {"url": url, "error": "Failed to fetch content or bad status code"}

            # Prepare metadata and document for transformers
            meta = self._prepare_meta(url)
            document = {"rawHtml": fetched_data.html, "metadata": {}}
            cleaned_document = self.crawl_transformers.execute_transformers(meta, document)
            
            # Use the Main Content Extractor to extract main content
            main_content = self.main_content_extractor.extract_main_content(url, cleaned_document)
            return {
                "url": url,
                "main_content_html": main_content["mc_html"],
                "main_content_markdown": main_content["mc_markdown"],
                "links": main_content["mc_links"],
            }
        except Exception as e:
            return {"url": url, "error": f"Error fetching main content: {e}"}


    def _prepare_meta(self, url: str) -> Dict:
        """Helper to prepare meta information."""
        return {
            "id": "fetch_url_and_clean_results",
            "url": url,
            "options": {"formats": ["html", "links", "markdown", "node_tree"], "actions": []},
            "logger": logger,
            "logs": [],
            "featureFlags": set(),
        }

    async def invoke(self) -> Dict[str, Any]:
        """
        Invoke the scraper to fetch main content for the given URL.

        :returns: The main content data or an error message.
        """
        try:
            result = await self.fetch_main_content(self.link)
            return result
        except Exception as e:
            return {"url": self.link, "error": f"Exception occurred: {str(e)}"}
