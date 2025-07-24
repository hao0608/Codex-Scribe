"""
This module contains the use case for answering a question based on the indexed repository.
"""

from src.domain.repositories.code_repository import CodeRepository
from src.domain.services.embedding_service import EmbeddingService
from src.infrastructure.llm.openai_client import OpenAIClient


class AnswerQuestionUseCase:
    """
    A use case for answering a natural language question using a RAG pipeline.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        code_repository: CodeRepository,
        llm_client: OpenAIClient,
    ):
        """
        Initializes the AnswerQuestionUseCase.

        Args:
            embedding_service: An instance of EmbeddingService to create embeddings.
            code_repository: An instance of CodeRepository to retrieve code chunks.
            llm_client: An instance of OpenAIClient to generate answers.
        """
        self.embedding_service = embedding_service
        self.code_repository = code_repository
        self.llm_client = llm_client

    def execute(self, query: str) -> str:
        """
        Executes the question-answering process.

        Args:
            query: The natural language question from the user.

        Returns:
            The generated answer.
        """
        print(f"Received query: {query}")

        # 1. Create an embedding for the query
        query_embedding = self.embedding_service.get_embedding(query)
        print("Generated query embedding.")

        # 2. Retrieve relevant code chunks
        retrieved_chunks = self.code_repository.search(query_embedding, top_k=5)
        if not retrieved_chunks:
            return "I couldn't find any relevant information in the codebase to answer your question."

        print(f"Retrieved {len(retrieved_chunks)} relevant chunks.")

        # 3. Build the context and prompt
        context = "\n\n---\n\n".join([chunk.content for chunk in retrieved_chunks])

        system_message = (
            "You are an expert software developer and AI assistant. "
            "Analyze the following code context to answer the user's question. "
            "Provide a clear, concise answer, and if relevant, include code snippets from the context."
        )

        prompt = f"""
        Context:
        ---
        {context}
        ---
        Question: {query}
        """

        # 4. Generate the answer
        print("Generating answer from LLM...")
        answer = self.llm_client.get_chat_completion(
            prompt=prompt,
            system_message=system_message,
        )

        return answer or "I was unable to generate an answer."
