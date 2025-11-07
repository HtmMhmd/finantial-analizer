import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Type

from crewai.tools import BaseTool
from landingai_ade import AsyncLandingAIADE
from pydantic import BaseModel, Field


class LandingAIExtractorInput(BaseModel):
    """Input schema for LandingAIDocumentExtractor."""

    file_path: str = Field(
        ..., description="Absolute path to the document file to process with LandingAI ADE."
    )


class LandingAIDocumentExtractor(BaseTool):
    """Tool that calls LandingAI ADE to extract structured data from documents."""

    name: str = "landing_ai_document_extractor"
    description: str = (
        "Uses LandingAI ADE to parse financial documents and returns structured JSON "
        "including text chunks, tables, key-value pairs, and provenance metadata."
    )
    args_schema: Type[BaseModel] = LandingAIExtractorInput

    def __init__(self) -> None:
        super().__init__()
        self._api_key = os.getenv("LANDINGAI_API_KEY")
        self._environment = os.getenv("LANDINGAI_ENDPOINT", "production")

    async def _async_extract(self, file_path: str) -> Dict[str, Any]:
        """Perform the asynchronous call to LandingAI ADE."""
        async with AsyncLandingAIADE(apikey=self._api_key, environment=self._environment) as client:

            response = await client.parse(document=Path(file_path), model="dpt-2-latest")

            return response.model_dump()

    def _run(self, file_path: str) -> Dict[str, Any]:
        """Run the tool synchronously, using a mock fallback if the API is unavailable."""
        try:
            return asyncio.run(self._async_extract(file_path))
        except Exception as exc:  # pragma: no cover - network fallback path
            # Provide a mock payload for local testing or when the API is unreachable.
            file_name = Path(file_path).name
            return {
                "metadata": {
                    "file_name": file_name,
                    "extraction_method": "mock_fallback",
                    "error": str(exc),
                },
                "chunks": [
                    {
                        "text": f"Mock extracted text from {file_name}",
                        "page": 1,
                        "bbox": [0, 0, 100, 100],
                        "confidence": 0.9,
                    }
                ],
                "tables": [],
                "key_value_pairs": [],
                "issues": [
                    {
                        "type": "api_unreachable",
                        "message": "LandingAI ADE unavailable; returned mock payload.",
                    }
                ],
            }
