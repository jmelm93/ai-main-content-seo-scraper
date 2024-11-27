````markdown
# AI Main Content SEO Scraper

This tool scrapes main content and metadata from URLs, leveraging AI and Playwright for accurate extraction even with JavaScript-heavy websites. It's designed for SEO analysis and content research, providing clean HTML, Markdown, extracted links, and key metadata.

## Features

- **AI-Powered Main Content Extraction:** Intelligently identifies and extracts the primary content of a page, filtering out noise like navigation and ads.
- **JavaScript Rendering:** Uses Playwright to execute JavaScript, ensuring accurate scraping of dynamic content.
- **Multiple Output Formats:** Provides extracted content in HTML, Markdown, and a structured JSONL node tree.
- **Metadata Extraction:** Gathers important SEO metadata like title, description, keywords, and Open Graph tags.
- **Link Extraction:** Extracts all links within the main content, facilitating further crawling and analysis.
- **Concurrent Processing:** Scrapes multiple URLs concurrently for faster results.
- **Customizable:** Configure proxy settings and other options via environment variables.

## File Structure

```
├── .env                                # Environment variables for configuration
├── main.py                             # Main script to run the scraper
├── requirements.txt                    # Project dependencies
└── src
    ├── __init__.py
    ├── config
    │   ├── __init__.py
    │   └── llm_config.py               # Loads and validates LLM configuration
    ├── core
    │   ├── __init__.py
    │   ├── mc_scraper_service.py       # Orchestrates main content scraping
    │   └── scraping_service.py         # Handles fetching web pages
    ├── models
    │   ├── __init__.py
    │   └── scraping_service_models.py  # Defines data models for scraping output
    ├── transformers
    │   ├── __init__.py
    │   ├── crawl_transformers.py       # Applies transformations to scraped data
    │   └── crawl_transformers_main_content.py # Extracts main content using AI
    └── utils
        ├── __init__.py
        └── crawl_transformer_utils.py  # Utility functions for HTML processing
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/ai-main-content-seo-scraper.git  # Replace with your repo URL
   cd ai-main-content-seo-scraper
   ```
````

2. **Create a virtual environment (recommended):**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright:**

   ```bash
   playwright install
   ```

5. **Set up environment variables:**

   Create a `.env` file in the root directory and add the following, replacing placeholders with your actual values:

   ```
   OPENAI_API_KEY=your_openai_api_key
   LLM_MODEL=gpt-4o  # Or another supported model
   LLM_TEMPERATURE=0.0 # Adjust as needed
   PROXY_HOST=your_proxy_host  # Optional
   PROXY_USERNAME=your_proxy_username # Optional
   PROXY_PASSWORD=your_proxy_password # Optional
   ```

## Usage

1. **Prepare your URL list:** Modify the `urls` list in `main.py` with the URLs you want to scrape.

2. **Run the scraper:**

   ```bash
   python main.py
   ```

3. **Output:** Scraped data will be saved in the `output` directory. For each URL, you'll find:

   - `{url}.md`: Main content in Markdown format.
   - `{url}_links.json`: Extracted links in JSON format.

## Configuration

- **LLM_MODEL:** The Large Language Model to use (e.g., `gpt-4o`, `gpt-3.5-turbo`). Defaults to `gpt-4o`.
- **LLM_TEMPERATURE:** Controls the randomness of the LLM's output. Lower values (e.g., 0.0) produce more deterministic results. Defaults to `0.0`.
- **PROXY_HOST, PROXY_USERNAME, PROXY_PASSWORD:** Optional proxy settings.
