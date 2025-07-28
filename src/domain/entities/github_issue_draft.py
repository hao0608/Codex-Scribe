"""
This module defines the Pydantic model for a GitHub issue draft.
"""

from pydantic import BaseModel, Field


class GitHubIssueDraft(BaseModel):
    """
    Represents a draft of a GitHub issue, ready to be created.
    """

    title: str = Field(..., description="The title of the GitHub issue.")
    body: str = Field(..., description="The body content of the GitHub issue.")
    labels: list[str] = Field(
        default_factory=list,
        description="A list of labels to apply to the GitHub issue.",
    )
