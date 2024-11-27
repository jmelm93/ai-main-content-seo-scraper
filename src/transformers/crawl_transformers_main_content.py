import json
import logging
import tiktoken

from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from lxml import html

from src.utils.crawl_transformer_utils import CrawlTransformerUtils
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


system_message = """
    # Extract Main Content Path from HTML Node Tree

    You will be provided with a JSON representation of an HTML document's node tree. Your task is to identify and return the CSS selector path to the top-level node that contains the primary page content, excluding navigation, headers, footers, and other non-primary elements.

    **Instructions:**
    1. Analyze the provided JSON node tree.
    2. Identify the primary content node (e.g., `article`, `main`, or similar).
    3. Construct a CSS selector path to that node using a specific and unambiguous format.
    4. Return the CSS selector path string. Do not include any additional text.

    **Example Input:**
    [
        {{path: /html/body/div/div/main/article, text: Some content here}},
        {{path: /html/body/div/div/nav, text: Navigation}},
    ]

    **Expected Output:**
    ```
    /html/body/div/div/main/article
    ```
"""


class CrawlTransformersMainContent:
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the CrawlTransformersMainContent with an LLM configuration.

        :param llm_config: Configuration parameters for the LLM model. Includes model, provider, api_key, and temperature.
        """
        self.llm_config = llm_config
        self.transformer_utils = CrawlTransformerUtils()
        self.max_tokens = 60000
        self.llm = ChatOpenAI(model=llm_config.get("model", "gpt-4o"), temperature=llm_config.get("temperature", 0.5), api_key=llm_config.get("api_key", ""))
        self.prompt_template = ChatPromptTemplate.from_messages(("system", system_message, "human", "{nodes}"))
        self.llm_chain = self.prompt_template | self.llm

    def _trim_node_tree(self, node_tree: List[Dict], max_tokens: Optional[int] = None) -> str:
        """
        Trim the node tree JSON to fit within the maximum token limit.

        :param node_tree: The input node tree as a list of dictionaries.
        :param max_tokens: Maximum number of tokens allowed for the JSON string.
        :return: A trimmed JSON string representation of the node tree.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        while True:
            json_string = json.dumps(node_tree)
            token_count = len(encoding.encode(json_string))
            max_tokens = max_tokens or self.max_tokens
            if token_count <= max_tokens:
                return json_string
            if node_tree:
                node_tree.pop()  # Remove one item from the end of the node tree
            else:
                raise ValueError("Node tree is empty. Cannot trim further.")


    def extract_main_content(self, url: str, cleaned_data_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract the main content path and HTML from the node tree.

        :param cleaned_data_obj: Object containing `html`, `node_tree`, and `page_target`.
        :return: Updated cleaned data object with main content details added.
        """
        try:
            
            full_html = cleaned_data_obj["html"]
            node_tree = cleaned_data_obj["node_tree"]
            
            # Trim the node tree to fit within token limits
            trimmed_json_string = self._trim_node_tree(node_tree)

            # Extract the main content selector
            result = self.llm_chain.invoke({"nodes": trimmed_json_string})
            
            # Clean the result path
            cleaned_result = self._clean_result_path(result.content.strip())

            # Extract the HTML for the main content
            main_content_html = self._get_main_content_html(full_html, cleaned_result)

            # Update the cleaned data object
            cleaned_data_obj["mc_path"] = cleaned_result
            cleaned_data_obj["mc_html"] = main_content_html
            cleaned_data_obj["mc_markdown"] = self.transformer_utils.html_to_markdown(main_content_html)
            cleaned_data_obj["mc_links"] = self.transformer_utils.extract_links(
                BeautifulSoup(main_content_html, "html.parser"), url
            )

            return cleaned_data_obj
        except Exception as e:
            logger.error(f"Error extracting main content: {e}")
            raise RuntimeError(f"Failed to extract main content: {e}")

    def _get_main_content_html(self, full_html: str, main_content_selector: str) -> str:
        """
        Extract the HTML content for the main content node using the CSS selector.

        :param full_html: Full HTML content of the page.
        :param main_content_selector: CSS selector path to the main content node.
        :return: HTML content of the main content node.
        """
        try:
            tree = html.fromstring(full_html)
            main_content_nodes = tree.xpath(main_content_selector)
        except Exception as e:
            raise ValueError(f"Failed to select main content nodes: {e}")

        if main_content_nodes:
            # Extract and concatenate HTML from selected nodes
            return "".join(html.tostring(node, encoding="unicode") for node in main_content_nodes)
        else:
            raise ValueError("Main content nodes not found in the HTML.")

    def _clean_result_path(self, result: str) -> str:
        """
        Clean the CSS selector path extracted by the LLM.

        :param result: Raw result string from the LLM.
        :return: Cleaned CSS selector path.
        """
        return result.replace("```", "").strip()
