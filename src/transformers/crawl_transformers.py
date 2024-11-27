import logging
from typing import Dict
from bs4 import BeautifulSoup
from src.utils.crawl_transformer_utils import CrawlTransformerUtils

logger = logging.getLogger(__name__)

class CrawlTransformers:
    def __init__(self):
        """Initializes the CrawlTransformers class with default configurations."""
        self.logger = logging.getLogger("CrawlTransformers")
        self.exclude_non_main_tags = [
            "header", "footer", "nav", "aside", ".header", ".top", ".navbar", "#header",
            ".footer", ".bottom", "#footer", ".sidebar", ".side", ".aside", "#sidebar",
            ".modal", ".popup", "#modal", ".overlay", ".ad", ".ads", ".advert", "#ad",
            ".lang-selector", ".language", "#language-selector", ".social", ".social-media",
            ".social-links", "#social", ".menu", ".navigation", "#nav", ".breadcrumbs",
            "#breadcrumbs", "#search-form", ".search", "#search", ".share", "#share",
            ".widget", "#widget", ".cookie", "#cookie"
        ]
        self.transformer_utils = CrawlTransformerUtils()

        # Register transformers dynamically for flexibility
        self.transformers = [
            self._derive_html_from_raw_html,
            self._derive_markdown_from_html,
            self._derive_metadata_from_html,
            self._derive_node_tree,
        ]

    def execute_transformers(self, meta: Dict, document: Dict) -> Dict:
        """
        Executes the transformation pipeline on the document.

        :param meta: Metadata for processing, including options and logging.
        :param document: Document dictionary containing rawHtml and additional fields.
        :return: Transformed document with additional fields like markdown, metadata, and node_tree.
        """
        for transformer in self.transformers:
            document["html"] = document["rawHtml"] # Initialize html field with rawHtml. will be updated later.
            try:
                if "rawHtml" not in document or not document["rawHtml"]:
                    raise ValueError("rawHtml is undefined or empty. Transformation cannot proceed.")
                soup = BeautifulSoup(document["html"], "html.parser")
                document = transformer(soup, meta, document)
            except Exception as e:
                self.logger.error(f"Error in transformer {transformer.__name__}: {e}")
        return document

    def _derive_html_from_raw_html(self, soup: BeautifulSoup, meta: Dict, document: Dict) -> Dict:
        """
        Cleans the raw HTML to remove unwanted elements.

        :param soup: BeautifulSoup object of the HTML.
        :param meta: Metadata with processing options.
        :param document: Document dictionary to update.
        :return: Updated document dictionary with cleaned HTML.
        """
        document["html"] = self.transformer_utils.remove_unwanted_elements(
            soup,
            exclude_tags=meta["options"].get("excludeTags", []),
            only_main_content=meta["options"].get("onlyMainContent", False),
            extra_removals=self.exclude_non_main_tags
        )
        return document

    def _derive_markdown_from_html(self, soup: BeautifulSoup, meta: Dict, document: Dict) -> Dict:
        """
        Converts HTML to Markdown format.

        :param soup: BeautifulSoup object of the HTML.
        :param meta: Metadata with processing options.
        :param document: Document dictionary to update.
        :return: Updated document dictionary with Markdown content.
        """
        document["full_markdown"] = self.transformer_utils.html_to_markdown(document["html"])
        return document

    def _derive_metadata_from_html(self, soup: BeautifulSoup, meta: Dict, document: Dict) -> Dict:
        """
        Extracts metadata from the HTML, such as title, description, and Open Graph tags.

        :param soup: BeautifulSoup object of the HTML.
        :param meta: Metadata with processing options.
        :param document: Document dictionary to update.
        :return: Updated document dictionary with metadata.
        """
        document["metadata"] = {
            **self.transformer_utils.extract_metadata(soup),
            **document.get("metadata", {})
        }
        return document

    def _derive_node_tree(self, soup: BeautifulSoup, meta: Dict, document: Dict) -> Dict:
        """
        Converts the HTML structure into a JSONL node tree representation.

        :param soup: BeautifulSoup object of the HTML.
        :param meta: Metadata with processing options.
        :param document: Document dictionary to update.
        :return: Updated document dictionary with node tree.
        """
        document["node_tree"] = self.transformer_utils.node_to_jsonl(soup)
        return document
