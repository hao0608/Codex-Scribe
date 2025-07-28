"""
This module defines the main FastAPI application and its endpoints.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.application.use_cases.create_issue_from_text import CreateIssueFromTextUseCase
from src.domain.services.github_service import GitHubServiceError
from src.infrastructure.database.chroma_client import ChromaDBClient
from src.infrastructure.github.pygithub_client import PyGitHubClient
from src.infrastructure.llm.openai_client import OpenAIClient

app = FastAPI(
    title="Codex-Scribe API",
    description="API for interacting with the Codex-Scribe AI agent.",
    version="0.1.0",
)


class AnalysisRequest(BaseModel):
    text: str


class AnalysisResponse(BaseModel):
    issue_url: str


@app.post("/api/v1/analyze-and-create-issue", response_model=AnalysisResponse)
def analyze_and_create_issue(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyzes a given text and creates a GitHub issue based on the analysis.
    """
    try:
        # In a real application, these dependencies would be injected.
        llm = OpenAIClient()
        embedding_service = OpenAIClient()
        code_repository = ChromaDBClient()
        github_service = PyGitHubClient()

        use_case = CreateIssueFromTextUseCase(
            llm=llm,
            embedding_service=embedding_service,
            code_repository=code_repository,
            github_service=github_service,
        )

        issue_url = use_case.execute(request.text)
        return AnalysisResponse(issue_url=issue_url)
    except GitHubServiceError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        ) from e
