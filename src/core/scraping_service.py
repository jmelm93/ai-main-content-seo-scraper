import os
import logging
from typing import Any, Dict, Optional
import aiohttp
from playwright.async_api import async_playwright
from src.transformers.crawl_transformers import CrawlTransformers
from src.models.scraping_service_models import ScrapingServiceOutput


logger = logging.getLogger(__name__)


class ScrapingService:
    def __init__(self):
        """Initializes the ScrapingService."""
        self.crawl_transformers = CrawlTransformers()
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'

    async def fetch_with_aiohttp(self, url: str, use_proxy: bool = False) -> Dict[str, Any]:
        """Fetch a page using aiohttp."""
        headers = {"User-Agent": self.user_agent}
        proxy = None
        if use_proxy:
            proxy = self._get_proxy()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, proxy=proxy, headers=headers) as response:
                    html = await response.text()
                    return {'url': url, 'content': html, 'status_code': response.status}
            except Exception as e:
                logger.error(f"Failed to fetch {url}: {e}")
                return {'url': url, 'content': None, 'status_code': 500}

    async def fetch_with_playwright(self, url: str, use_proxy: bool = False) -> Dict[str, Any]:
        """Fetch a page using Playwright for JavaScript rendering."""
        try:
            async with async_playwright() as p:
                browser_type = p.chromium  # Choose chromium, firefox, or webkit
                launch_options = {}

                if use_proxy:
                    proxy = self._get_proxy()
                    launch_options['proxy'] = {
                        'server': proxy['server'],
                        'username': proxy['username'],
                        'password': proxy['password'],
                    }

                browser = await browser_type.launch(**launch_options)
                context = await browser.new_context(user_agent=self.user_agent)
                page = await context.new_page()
                response = await page.goto(url)
                content = await page.content()
                status_code = response.status
                await browser.close()
                return {'url': url, 'content': content, 'status_code': status_code}

        except Exception as e:
            logger.error(f"Error fetching with Playwright: {e}")
            return {'url': url, 'content': None, 'status_code': 500}

    async def crawl_page(self, url: str, render_js: bool = True) -> Dict[str, Any]:
        """Crawl a page, optionally rendering JavaScript."""
        logger.info(f"Crawling {url} with {'JS rendering' if render_js else 'no JS rendering'}")
        try:
            if render_js:
                return await self.fetch_with_playwright(url)
            else:
                return await self.fetch_with_aiohttp(url)
        except Exception as e:
            logger.error(f"Error during crawl: {e}")
            return {'url': url, 'content': None, 'status_code': 500}

    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """Retrieve proxy configuration from environment variables."""
        host = os.getenv("PROXY_HOST")
        username = os.getenv("PROXY_USERNAME")
        password = os.getenv("PROXY_PASSWORD")
        if not host or not username or not password:
            return None
        return {'server': f'http://{host}', 'username': username, 'password': password}

    async def fetch_url(self, url: str, render_js: bool = True) -> ScrapingServiceOutput:
        """Fetches a URL and returns the page content."""
        result = await self.crawl_page(url, render_js)
        return ScrapingServiceOutput(
            link=result['url'],
            status_code=result['status_code'],
            html=result['content'],
        )