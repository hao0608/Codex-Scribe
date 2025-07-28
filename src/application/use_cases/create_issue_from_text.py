"""
This module defines the use case for creating a GitHub issue from a given text.
"""

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable

from src.domain.repositories.code_repository import CodeRepository
from src.domain.services.embedding_service import EmbeddingService
from src.domain.services.github_service import GitHubIssueDraft, GitHubService


class CreateIssueFromTextUseCase:
    """
    This use case handles the logic for creating a GitHub issue from a raw text input.
    """

    def __init__(
        self,
        llm: RunnableSerializable[dict[str, str], str],
        embedding_service: EmbeddingService,
        code_repository: CodeRepository,
        github_service: GitHubService,
    ):
        self.llm = llm
        self.embedding_service = embedding_service
        self.code_repository = code_repository
        self.github_service = github_service
        self.parser: PydanticOutputParser[GitHubIssueDraft] = PydanticOutputParser(
            pydantic_object=GitHubIssueDraft
        )

    def execute(self, text: str) -> str:
        """
        Analyzes the text, generates a structured issue draft, and creates it on GitHub.

        Args:
            text: The raw text input (e.g., user feedback).

        Returns:
            The URL of the newly created GitHub issue.
        """
        prompt_template = """
        You are an expert at analyzing user feedback and creating high-quality GitHub issues.
        Your primary goal is to accurately reflect the user's report. Use the code context for technical insights, but do not invent details that the user did not provide.

        **IMPORTANT**:
        1.  Always include the 'ai-draft' and 'needs-review' labels in your response.
        2.  The issue body MUST start with a "User Report" section that quotes the user's feedback verbatim.

        User Feedback:
        {text}

        Relevant Code Context:
        {context}

        Format Instructions:
        {format_instructions}
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text", "context"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        # 1. Retrieve relevant code context
        query_embedding = self.embedding_service.get_embedding(text)
        retrieved_chunks = self.code_repository.search(query_embedding, top_k=5)
        context = "\n---\n".join([chunk.content for chunk in retrieved_chunks])

        # 2. Create the chain and invoke it
        chain = prompt | self.llm | self.parser
        issue_draft = chain.invoke({"text": text, "context": context})

        # 3. Create the issue on GitHub
        issue_url = self.github_service.create_issue(issue_draft)
        return issue_url
