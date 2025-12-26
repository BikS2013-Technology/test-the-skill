"""
Azure OpenAI Configuration Module

This module provides Azure OpenAI model initialization for LangGraph ReAct Agent examples.
It validates that all required environment variables are set.
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load environment variables from .env file if it exists
load_dotenv()


def validate_environment():
    """
    Ensure all required Azure OpenAI environment variables are set.

    Required variables:
    - AZURE_OPENAI_API_KEY: Azure OpenAI API key
    - AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL
    - AZURE_OPENAI_API_VERSION: Azure OpenAI API version
    - AZURE_OPENAI_DEPLOYMENT: Azure OpenAI deployment name
    - TAVILY_API_KEY: Tavily Search API key

    Raises:
        ValueError: If any required environment variable is missing.
    """
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT",
        "TAVILY_API_KEY"
    ]

    missing = [var for var in required_vars if not os.environ.get(var)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {missing}. "
            "Please set these in your .env file or environment."
        )


def get_azure_model() -> AzureChatOpenAI:
    """
    Create and return an AzureChatOpenAI model instance.

    Returns:
        AzureChatOpenAI: Configured Azure OpenAI chat model.

    Raises:
        ValueError: If required environment variables are not set.
    """
    validate_environment()

    return AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"]
    )


def get_tavily_api_key() -> str:
    """
    Get the Tavily API key from environment variables.

    Returns:
        str: The Tavily API key.

    Raises:
        ValueError: If TAVILY_API_KEY is not set.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("Missing required environment variable: TAVILY_API_KEY")
    return api_key
