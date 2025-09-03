# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Set up environment variables
cp .env.example .env  # Then edit .env with your API keys
```

### Database Services
```bash
# Start Neo4j service (required for graph database)
docker-compose up -d neo4j

# Index a repository for code understanding
python scripts/index_repository.py --path /path/to/your/repository
```

### Running the Application
```bash
# Start the FastAPI server
uvicorn src.presentation.api.main:app --reload

# Start the Streamlit UI (optional)
streamlit run src.presentation.web.streamlit_app.py
```

### Code Quality & Testing
```bash
# Format code
black src/ tests/ scripts/

# Sort imports
isort src/ tests/ scripts/

# Type checking
mypy src/

# Lint code
ruff check src/ tests/ scripts/ --fix

# Run tests
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m external_deps # Tests requiring external services

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Architecture Overview

This is an AI-powered code intelligence platform built with **Clean Architecture** principles, featuring a hybrid retrieval system that combines vector search and graph queries for deep code understanding.

### Core Architecture Layers

**Domain Layer** (`src/domain/`):
- `entities/`: Core data models (CodeChunk, GitHubIssueDraft, Graph entities)
- `repositories/`: Abstract interfaces for data access
- `services/`: Business logic services

**Application Layer** (`src/application/`):
- `use_cases/`: Business use cases (AnswerQuestion, CreateIssueFromText, IndexRepository)
- `interfaces/`: Application service interfaces

**Infrastructure Layer** (`src/infrastructure/`):
- `database/`: ChromaDB (vector) and Neo4j (graph) implementations
- `llm/`: OpenAI and other LLM client implementations
- `github/`: PyGithub client for GitHub API integration
- `parser/`: Tree-sitter based code parsing

**Presentation Layer** (`src/presentation/`):
- `api/`: FastAPI REST endpoints
- `web/`: Streamlit UI application
- `cli/`: Command-line interface

### Key Technologies

- **AI/ML**: LangChain, OpenAI GPT-4o, Anthropic Claude 3.5, Google Gemini
- **Embeddings**: OpenAI text-embedding-3-large, Voyage AI voyage-code-2
- **Databases**: ChromaDB (vector search), Neo4j (knowledge graph)
- **Code Parsing**: tree-sitter for AST parsing
- **Web Framework**: FastAPI with Pydantic validation
- **UI**: Streamlit for interactive interface

## Development Guidelines

### Code Style Requirements
- **Formatting**: Black (line length: 88)
- **Import sorting**: isort (black profile)
- **Type hints**: Mandatory for all functions and class attributes using mypy
- **Linting**: Ruff for code quality
- **Docstrings**: Google style format with Args, Returns, Raises sections

### API Design Principles
- **RESTful**: Resource-oriented design with standard HTTP methods
- **JSON**: snake_case for all field names
- **Validation**: Pydantic models for request/response validation
- **Error handling**: Structured error responses with proper HTTP status codes

### AI/LLM Integration Best Practices
- **Structured output**: Always use Pydantic models or JSON schema for LLM responses
- **Context injection**: Provide relevant code snippets and context in prompts
- **Validation**: Never trust LLM output without validation
- **RAG pattern**: Prefer retrieved information over model internal knowledge

## Key Use Cases

1. **IndexRepository**: Processes code repositories using tree-sitter, creates embeddings, and builds knowledge graphs
2. **AnswerQuestion**: Hybrid retrieval system that routes queries to vector search or graph queries based on intent
3. **CreateIssueFromText**: Analyzes user feedback and automatically generates GitHub issue drafts

## Environment Dependencies

- **Python**: 3.12+
- **External Services**:
  - OpenAI API (for LLM and embeddings)
  - Neo4j database (via Docker)
  - GitHub API (for issue creation)
- **Required Environment Variables**: Configure in `.env` file for API keys and database connections
