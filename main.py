import os
import json
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from asyncio import run
from dotenv import load_dotenv

from src.core.mc_scraper_service import MCScraperService

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Input URL list for testing
urls = [
    "https://www.wordstream.com/seo",
    "https://www.semrush.com/blog/seo-tips/",
    "https://www.semrush.com/blog/google-seo/",
    "https://www.orbitmedia.com/blog/seo-best-practices/",
    "https://marketingtoolbox.ucdavis.edu/departments/web/search-engine-optimization/seo-best-practices",
    "https://keywordseverywhere.com/seo-metrics.html",
    "https://dorik.com/blog/seo-best-practices",
    "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
]


def process_results(results: List[Dict[str, Any]]) -> None:
    """Processes and saves the results to files."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    for result in results:
        filename_base = result['url'].replace('/', '_').replace(':', '_')

        if "error" not in result:
            # Save main content as markdown
            with open(os.path.join(output_dir, f"{filename_base}.md"), "w", encoding="utf-8") as f:
                f.write(result.get("main_content_markdown", ""))

            # Save extracted links as JSON
            with open(os.path.join(output_dir, f"{filename_base}_links.json"), "w", encoding="utf-8") as f:
                json.dump(result.get("links", []), f, indent=4)
        else:
            logger.error(f"Failed to process {result['url']}: {result['error']}")

async def scrape_url(url: str) -> Dict[str, Any]:
    """Asynchronously scrapes a URL using MCScraperService."""
    scraper = MCScraperService(link=url)
    return await scraper.invoke()


def main():
    """Main function to orchestrate crawling and extraction."""
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks for each URL
        futures = [executor.submit(run, scrape_url(url)) for url in urls]

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                logger.error(f"A task generated an exception: {exc}")

    process_results(results)


if __name__ == "__main__":
    main()
