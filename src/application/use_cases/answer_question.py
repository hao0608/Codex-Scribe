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
        try:
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
                "你是一位專業的軟體開發專家與 AI 助理。"
                "請分析以下程式碼上下文來回答使用者的問題。"
                "請提供清晰、簡潔的答案，並在適當時附上相關的程式碼片段。"
                "請務必使用繁體中文（台灣）進行回覆。"
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
        except Exception as e:
            print(f"An unexpected error occurred during question answering: {e}")
            # In a real app, you might want to return a more user-friendly error message.
            return "Sorry, an error occurred while processing your request."
