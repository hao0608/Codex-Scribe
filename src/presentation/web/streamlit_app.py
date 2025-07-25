"""
This module provides a Streamlit web interface for the Code Question Answering Bot.
"""

import os
import sys

import streamlit as st
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.application.use_cases.answer_question import AnswerQuestionUseCase
from src.infrastructure.database.chroma_client import ChromaDBClient
from src.infrastructure.llm.openai_client import OpenAIClient


def setup_dependencies() -> AnswerQuestionUseCase:
    """
    Sets up the dependency injection for the application.
    In a real application, this would be handled by a DI container.
    """
    load_dotenv()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error(
            "OPENAI_API_KEY environment variable not set. Please create a .env file."
        )
        st.stop()

    embedding_service = OpenAIClient()
    code_repository = ChromaDBClient()
    llm_client = OpenAIClient()

    answer_question_use_case = AnswerQuestionUseCase(
        embedding_service=embedding_service,
        code_repository=code_repository,
        llm_client=llm_client,
    )
    return answer_question_use_case


def main() -> None:
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(page_title="Codex-Scribe Q&A", layout="wide")

    st.title("Codex-Scribe: Code Question Answering Bot 💬")
    st.markdown(
        "Ask a question about your codebase, and the AI will try to answer based on the indexed context."
    )

    try:
        answer_question_use_case = setup_dependencies()
    except ValueError as e:
        st.error(e)
        st.stop()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is your question?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            response = answer_question_use_case.execute(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
