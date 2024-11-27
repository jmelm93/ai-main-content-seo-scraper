from typing import List, Dict, Optional
from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import urljoin
import html2text
import json

class CrawlTransformerUtils:
    """
    Utility class for transforming HTML content.
    """
    
    def __init__(self):
        self.non_essential_tags = [
            "script", "style", "meta", "link", "iframe", "svg",
            "noscript", "figure", "picture", "img", "source", "button",
            "input", "nav", "footer", "header", "aside"
        ]
    
    @staticmethod
    def html_to_markdown(html_content: str) -> str:
        """
        Converts HTML content to Markdown format.
        
        :param html_content: Raw HTML string.
        :return: Markdown formatted string.
        """
        converter = html2text.HTML2Text()
        converter.ignore_links = False  # Include links in the output
        return converter.handle(html_content)

    @staticmethod
    def remove_unwanted_elements(
        soup: BeautifulSoup, 
        exclude_tags: List[str], 
        only_main_content: bool, 
        extra_removals: List[str]
    ) -> str:
        """
        Removes unwanted elements from the HTML content.
        
        :param soup: BeautifulSoup object of the HTML.
        :param exclude_tags: Tags to exclude from the HTML.
        :param only_main_content: Whether to remove non-main content.
        :param extra_removals: Additional CSS selectors for removal.
        :return: Cleaned HTML as a string.
        """
        # Remove script-like and specified tags
        for tag in ["script", "style", "noscript", "meta", "head"] + exclude_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Optionally remove non-main content
        if only_main_content:
            for tag in extra_removals:
                for element in soup.select(tag):
                    element.decompose()

        return soup.decode_contents()

    @staticmethod
    def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extracts absolute links from the HTML content.
        
        :param soup: BeautifulSoup object of the HTML.
        :param base_url: Base URL to resolve relative links.
        :return: List of absolute URLs.
        """
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("http://", "https://")):
                links.add(href)
            elif href.startswith("/"):
                links.add(urljoin(base_url, href))
            elif not href.startswith(("#", "mailto:")):
                links.add(urljoin(base_url, href))
            elif href.startswith("mailto:"):
                links.add(href)

        return list(links)

    @staticmethod
    def extract_metadata(soup: BeautifulSoup) -> Dict:
        """
        Extracts metadata such as title, description, keywords, and Open Graph tags.
        
        :param soup: BeautifulSoup object of the HTML.
        :return: Dictionary containing metadata.
        """
        metadata = {
            "title": soup.title.string if soup.title else None,
            "description": (soup.find("meta", attrs={"name": "description"}) or {}).get("content"),
            "keywords": (soup.find("meta", attrs={"name": "keywords"}) or {}).get("content"),
            "language": soup.html.get("lang") if soup.html else None,
        }

        # Add Open Graph metadata
        for tag in ["og:title", "og:description", "og:url", "og:image"]:
            og_meta = soup.find("meta", property=tag)
            if og_meta:
                metadata[tag.replace("og:", "")] = og_meta.get("content")

        return metadata

    def node_to_jsonl(
        self,
        node,
        non_essential_tags: Optional[List[str]] = None,
        path_prefix: str = "",
    ) -> List[str]:
        """
        Converts an HTML node tree to a JSONL format.
        
        :param node: A BeautifulSoup node to process.
        :param non_essential_tags: Tags to exclude from the JSONL.
        :param path_prefix: Path prefix for the current node.
        :return: List of JSONL strings.
        """
        if non_essential_tags is None:
            non_essential_tags = self.non_essential_tags

        lines = []

        if isinstance(node, NavigableString):
            if isinstance(node, Comment):
                return []
            else:
                text = str(node).strip()
                if text:
                    current_path = path_prefix.lstrip("/[document]")
                    data = {
                        "path": current_path,
                        "text": text,
                    }
                    lines.append(json.dumps(data, ensure_ascii=False))
                return lines

        elif hasattr(node, "name"):
            if node.name.lower() in non_essential_tags:
                return []
            current_path = f"{path_prefix}/{node.name}" if path_prefix else f"/{node.name}"

            # Process child nodes
            for child in node.contents:
                child_lines = self.node_to_jsonl(child, non_essential_tags, current_path)
                lines.extend(child_lines)

            return lines

        return []

    def node_to_dict(
        self,
        node,
        non_essential_tags: Optional[List[str]] = None,
    ) -> Optional[Dict]:
        """
        Converts an HTML node tree to a dictionary format.
        
        :param node: A BeautifulSoup node to process.
        :param non_essential_tags: Tags to exclude from the JSONL.
        :return: Dictionary representation of the HTML.
        """
        
        if non_essential_tags is None:
            non_essential_tags = self.non_essential_tags
            
        if isinstance(node, NavigableString):
            if isinstance(node, Comment):
                # Skip comment nodes
                return None
            else:
                # Handle text nodes
                text = str(node).strip()
                if text:
                    # Include only the first 50 characters
                    return {'type': 'text', 'text': text}
                else:
                    return None  # Skip empty text nodes

        elif hasattr(node, 'name'):
            # Exclude non-essential tags
            if node.name.lower() in non_essential_tags:
                return None

            result = {'type': 'element', 'name': node.name}

            # include all attributes
            if node.attrs:
                result['attrs'] = node.attrs

            # Process all children without limiting
            children = []
            for child in node.contents:
                child_dict = self.node_to_dict(child)
                if child_dict:
                    children.append(child_dict)
            if children:
                result['children'] = children
            return result

        else:
            return None  # Unknown node type