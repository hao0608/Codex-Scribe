"""
This module contains the use case for answering a question based on the indexed repository.
"""

import re
from typing import Any

from src.application.use_cases.graph_query import GraphQueryUseCase
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
        graph_query_use_case: GraphQueryUseCase,
    ):
        """
        Initializes the AnswerQuestionUseCase.
        """
        self.embedding_service = embedding_service
        self.code_repository = code_repository
        self.llm_client = llm_client
        self.graph_query_use_case = graph_query_use_case

    def _plan_task(self, query: str) -> tuple[str, dict[str, Any] | None]:
        """
        A simple task planner to decide whether to use vector search or graph query.
        """
        # Simple keyword-based routing
        if re.search(r"who calls|callers of|被誰呼叫", query, re.IGNORECASE):
            # Example: "Who calls the 'process_payment' function?"
            match = re.search(r"['\"](.+)['\"]", query)
            if match:
                return "graph_query_callers", {"function_name": match.group(1)}

        if re.search(r"methods in|方法在", query, re.IGNORECASE):
            # Example: "What methods are in the 'User' class?"
            match = re.search(r"['\"](.+)['\"]", query)
            if match:
                return "graph_query_methods", {"class_name": match.group(1)}

        if re.search(r"what methods are in the", query, re.IGNORECASE):
            match = re.search(r"['\"](.+)['\"]", query)
            if match:
                return "graph_query_methods", {"class_name": match.group(1)}

        # Default to vector search
        return "vector_search", None

    def execute(self, query: str) -> str:
        """
        Executes the question-answering process.
        """
        try:
            print(f"Received query: {query}")

            task, params = self._plan_task(query)
            print(f"Planned task: {task}")

            context = ""
            if task == "vector_search":
                # 1. Create an embedding for the query
                query_embedding = self.embedding_service.get_embedding(query)
                print("Generated query embedding.")

                # 2. Retrieve relevant code chunks
                retrieved_chunks = self.code_repository.search(query_embedding, top_k=5)
                if not retrieved_chunks:
                    return "I couldn't find any relevant information in the codebase to answer your question."

                print(f"Retrieved {len(retrieved_chunks)} relevant chunks.")
                context = "\n\n---\n\n".join(
                    [chunk.content for chunk in retrieved_chunks]
                )

            elif task == "graph_query_callers" and params:
                results = self.graph_query_use_case.get_function_callers(
                    params["function_name"]
                )
                if results:
                    context = f"The function '{params['function_name']}' is called by: {results}"
                else:
                    context = f"I couldn't find any callers for the function '{params['function_name']}' in the indexed codebase."

            elif task == "graph_query_methods" and params:
                results = self.graph_query_use_case.get_methods_in_class(
                    params["class_name"]
                )
                if results:
                    context = f"The class '{params['class_name']}' contains the following methods: {results}"
                else:
                    context = f"I couldn't find any methods for the class '{params['class_name']}' in the indexed codebase."

            # 3. Build the prompt
            system_message = (
                "你是一位專業的軟體開發專家與 AI 助理。"
                "請分析以下上下文來回答使用者的問題。"
                "上下文可能是程式碼片段，也可能是知識圖譜的查詢結果。"
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
            return "Sorry, an error occurred while processing your request."
