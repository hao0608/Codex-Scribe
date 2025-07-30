"""
This module contains the use case for answering a question based on the indexed repository.
"""

import json
import re
from typing import Any, cast

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

    def _build_classification_prompt(self, query: str) -> str:
        """
        Builds the prompt for the LLM to classify the query intent.
        """
        return f"""
        You are an expert query classifier. Analyze the user's query and determine the most appropriate search method.

        Examples:
        - "Who calls the 'process_payment' function?" -> {{"type": "graph_query_callers", "entity": "process_payment", "confidence": 0.9}}
        - "誰調用了 'authenticate' 方法？" -> {{"type": "graph_query_callers", "entity": "authenticate", "confidence": 0.9}}
        - "What methods are in the User class?" -> {{"type": "graph_query_methods", "entity": "User", "confidence": 0.9}}
        - "User 類別包含哪些方法？" -> {{"type": "graph_query_methods", "entity": "User", "confidence": 0.9}}
        - "How does authentication work?" -> {{"type": "vector_search", "entity": null, "confidence": 0.95}}
        - "解釋一下支付流程" -> {{"type": "vector_search", "entity": null, "confidence": 0.95}}

        Query: "{query}"

        Return a JSON object with the following schema:
        {{
            "type": "vector_search" | "graph_query_callers" | "graph_query_methods",
            "entity": string | null,
            "confidence": float (0.0 to 1.0)
        }}
        """

    def _classify_query_intent(self, query: str) -> dict[str, Any]:
        """
        Classifies the user's query to determine the search strategy.
        Uses an LLM for primary classification and falls back to regex.
        """
        # 1. Use LLM for classification
        prompt = self._build_classification_prompt(query)
        try:
            response = self.llm_client.get_chat_completion(
                prompt, system_message="You are a JSON-outputting classifier."
            )
            if response:
                result = json.loads(response)
                if result.get("confidence", 0) > 0.75:
                    print(f"LLM classification successful: {result}")
                    return result
        except (json.JSONDecodeError, TypeError) as e:
            print(f"LLM classification failed or returned invalid JSON: {e}")

        # 2. Fallback to regex if LLM fails or has low confidence
        print("Falling back to regex-based classification.")
        if re.search(r"who calls|callers of|被誰呼叫", query, re.IGNORECASE):
            match = re.search(r"['\"](.+)['\"]", query)
            if match:
                return {"type": "graph_query_callers", "entity": match.group(1)}

        if re.search(
            r"methods in|方法在|what methods are in the", query, re.IGNORECASE
        ):
            match = re.search(r"['\"](.+)['\"]", query)
            if match:
                return {"type": "graph_query_methods", "entity": match.group(1)}

        return {"type": "vector_search", "entity": None}

    def _determine_query_complexity(self, query: str) -> bool:
        """
        Determines if a query is complex based on a few heuristics.
        """
        # Heuristic 1: Query length
        is_long_query = len(query.split()) > 10

        # Heuristic 2: Presence of interrogative words that imply complexity
        complex_keywords = [
            "how",
            "why",
            "explain",
            "describe",
            "analyze",
            "如何",
            "為什麼",
            "解釋",
            "描述",
            "分析",
        ]
        has_complex_keyword = any(
            keyword in query.lower() for keyword in complex_keywords
        )

        # Heuristic 3: Multiple questions
        has_multiple_questions = query.count("?") > 1

        # Consider the query complex if at least two heuristics are met
        return [is_long_query, has_complex_keyword, has_multiple_questions].count(
            True
        ) >= 2

    def _get_optimal_top_k(self, query: str) -> int:
        """
        Returns the optimal top_k value based on query complexity.
        """
        return 10 if self._determine_query_complexity(query) else 5

    def execute(self, query: str) -> str:
        """
        Executes the question-answering process.
        """
        try:
            print(f"Received query: {query}")

            intent = self._classify_query_intent(query)
            task_type = intent.get("type", "vector_search")
            entity = intent.get("entity")
            print(f"Planned task: {task_type}, Entity: {entity}")

            context = ""
            if task_type == "vector_search":
                query_embedding = self.embedding_service.get_embedding(query)
                print("Generated query embedding.")

                # 2. Retrieve relevant code chunks
                top_k = self._get_optimal_top_k(query)
                print(f"Using top_k={top_k} based on query complexity.")
                retrieved_chunks = self.code_repository.search(
                    query_embedding, top_k=top_k
                )

                if not retrieved_chunks:
                    return "I couldn't find any relevant information in the codebase to answer your question."
                print(f"Retrieved {len(retrieved_chunks)} relevant chunks.")
                context = "\n\n---\n\n".join(
                    [chunk.content for chunk in retrieved_chunks]
                )

            elif task_type == "graph_query_callers" and entity:
                results = self.graph_query_use_case.get_function_callers(
                    cast(str, entity)
                )
                if results:
                    context = f"The function '{entity}' is called by: {results}"
                else:
                    context = f"I couldn't find any callers for the function '{entity}' in the indexed codebase."

            elif task_type == "graph_query_methods" and entity:
                results = self.graph_query_use_case.get_methods_in_class(
                    cast(str, entity)
                )
                if results:
                    context = f"The class '{entity}' contains the following methods: {results}"
                else:
                    context = f"I couldn't find any methods for the class '{entity}' in the indexed codebase."

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
