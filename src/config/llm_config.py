import os
from typing import Dict, Any

def get_llm_config() -> Dict[str, Any]:
    """Retrieves and validates LLM configuration parameters from environment variables."""

    llm_config: Dict[str, Any] = {
        "model": os.getenv("LLM_MODEL", "gpt-4o"),  # Default to gpt-4o if not set
        "provider": os.getenv("LLM_PROVIDER", "openai"),  # Default to OpenAI
        "api_key": os.getenv("OPENAI_API_KEY", ""),  # No default for API key; must be set
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.0")),  # Default temperature 0.0
    }

    if not llm_config["api_key"]:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")

    return llm_config
