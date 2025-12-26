"""
Test Script 07: Structured Output Examples
Tests structured output functionality from the LangChain Fundamentals Guide.
"""

import os
from langchain_openai import AzureChatOpenAI

# Validate required environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT"
]

for var in required_vars:
    if not os.environ.get(var):
        raise ValueError(f"{var} environment variable is required")


def get_model():
    """Get configured Azure OpenAI model."""
    return AzureChatOpenAI(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"]
    )


def test_pydantic_structured_output():
    """
    Test Example: Using Pydantic Models (Document Section: Structured Output)
    From lines 878-892
    """
    print("\n=== Test: Pydantic Structured Output ===")

    from pydantic import BaseModel, Field

    class Movie(BaseModel):
        """A movie with details."""
        title: str = Field(..., description="The title of the movie")
        year: int = Field(..., description="The year the movie was released")
        director: str = Field(..., description="The director of the movie")
        rating: float = Field(..., description="The movie's rating out of 10")

    model = get_model()
    model_with_structure = model.with_structured_output(Movie)
    response = model_with_structure.invoke("Provide details about the movie Inception")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    print(f"Title: {response.title}")
    print(f"Year: {response.year}")
    print(f"Director: {response.director}")
    print(f"Rating: {response.rating}")
    return True


def test_typeddict_structured_output():
    """
    Test Example: Using TypedDict (Document Section: Structured Output)
    From lines 896-910
    """
    print("\n=== Test: TypedDict Structured Output ===")

    from typing_extensions import TypedDict, Annotated

    class MovieDict(TypedDict):
        """A movie with details."""
        title: Annotated[str, ..., "The title of the movie"]
        year: Annotated[int, ..., "The year the movie was released"]
        director: Annotated[str, ..., "The director of the movie"]
        rating: Annotated[float, ..., "The movie's rating out of 10"]

    model = get_model()
    model_with_structure = model.with_structured_output(MovieDict)
    response = model_with_structure.invoke("Provide details about the movie Inception")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    print(f"Title: {response['title']}")
    print(f"Year: {response['year']}")
    print(f"Director: {response['director']}")
    print(f"Rating: {response['rating']}")
    return True


def test_json_schema_structured_output():
    """
    Test Example: Using JSON Schema (Document Section: Structured Output)
    From lines 914-947
    """
    print("\n=== Test: JSON Schema Structured Output ===")

    json_schema = {
        "title": "Movie",
        "description": "A movie with details",
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the movie"
            },
            "year": {
                "type": "integer",
                "description": "The year the movie was released"
            },
            "director": {
                "type": "string",
                "description": "The director of the movie"
            },
            "rating": {
                "type": "number",
                "description": "The movie's rating out of 10"
            }
        },
        "required": ["title", "year", "director", "rating"]
    }

    model = get_model()
    model_with_structure = model.with_structured_output(
        json_schema,
        method="json_schema"
    )
    response = model_with_structure.invoke("Provide details about the movie Inception")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    return True


def test_include_raw_response():
    """
    Test Example: Include Raw Response (Document Section: Structured Output)
    From lines 951-962
    """
    print("\n=== Test: Include Raw Response ===")

    from pydantic import BaseModel, Field

    class Movie(BaseModel):
        """A movie with details."""
        title: str = Field(..., description="The title of the movie")
        year: int = Field(..., description="The year the movie was released")
        director: str = Field(..., description="The director of the movie")
        rating: float = Field(..., description="The movie's rating out of 10")

    model = get_model()
    model_with_structure = model.with_structured_output(Movie, include_raw=True)
    response = model_with_structure.invoke("Provide details about the movie Inception")
    print(f"Response type: {type(response)}")
    print(f"Response keys: {response.keys()}")
    print(f"Raw: {type(response['raw'])}")
    print(f"Parsed: {response['parsed']}")
    print(f"Parsing error: {response['parsing_error']}")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Structured Output Tests")
    print("=" * 60)

    tests = [
        ("Pydantic Structured Output", test_pydantic_structured_output),
        ("TypedDict Structured Output", test_typeddict_structured_output),
        ("JSON Schema Structured Output", test_json_schema_structured_output),
        ("Include Raw Response", test_include_raw_response),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "PASSED" if success else "FAILED"))
        except Exception as e:
            results.append((name, f"ERROR: {e}"))

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    for name, result in results:
        print(f"{name}: {result}")
