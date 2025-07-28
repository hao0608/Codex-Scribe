# Welcome to Codex-Scribe

**Codex-Scribe: Your AI-Powered Code Intelligence Platform**

`Codex-Scribe` is an advanced AI agent designed to deeply understand GitHub projects. It not only reads and comprehends code but also parses its structure, dependencies, and semantics, transforming your codebase into a queryable and interactive knowledge base.

---

## ✨ Core Features

- **🧠 Hybrid Retrieval**: Combines **vector search** (to understand "what") and **graph queries** (to understand "how it's related") for unprecedented insight into your code.
- **🕸️ Deep Knowledge Graph**: Automatically transforms your codebase into a knowledge graph, allowing you to visualize and query complex relationships between classes, functions, and modules.
- **🤖 Intelligent Agent**: Capable of autonomously deciding which retrieval strategy to use based on the nature of the question to get the most accurate answer.
- **🔄 Automated Workflow**: Can be triggered via API or GitHub Webhooks to automatically analyze user feedback, code commits, and generate structured GitHub issue drafts.
- **🔌 Multi-Model Support**: A flexible architecture supports various top-tier LLMs (like GPT-4o, Claude 3.5) and embedding models, choosing the best tool for different tasks.

---

## 🚀 Quick Start

For a detailed setup guide, please see the [Setup Guide](implementation/setup-guide.md).

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/hao0608/Codex-Scribe.git
    cd Codex-Scribe
    ```
2.  **Install dependencies**:
    ```bash
    poetry install
    ```
3.  **Configure environment variables**:
    ```bash
    cp .env.example .env
    # (Edit .env and fill in your API keys)
    ```
4.  **Run the application**:
    ```bash
    streamlit run src/presentation/web/streamlit_app.py
    ```

---

## 📖 Documentation Sections

- **[Architecture](architecture/system-overview.md)**: Learn about the system design, data flow, and security considerations.
- **[Development](development/git-workflow.md)**: Find out about our development process, including Git workflow and phase planning.
- **[Implementation](implementation/setup-guide.md)**: Get detailed instructions on setting up, deploying, and testing the project.
- **[Research](research/literature-review.md)**: Explore the research and technology comparisons that inform our approach.
- **[Technical](technical/ai-model-specs.md)**: Dive into the technical specifications, including AI models, coding standards, and database schemas.

---

## Current Status: Phase 1 - MVP Complete

We have successfully completed the Minimum Viable Product (MVP) phase. The core functionality of code indexing and question answering via a RAG pipeline is now in place.

**Next Up**: Phase 2 - Automation, where we will focus on integrating with GitHub to automate issue creation and analysis.
