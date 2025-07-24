# Component Style Guide

## 1. 概述

本文件定義了 `Codex-Scribe` 專案中所有程式碼元件的設計規範和程式碼風格。遵循此指南有助於確保程式碼的一致性、可讀性和可維護性。

**目標讀者**: 所有參與此專案的開發者和 AI 代理程式。

## 2. 通用原則

- **單一職責原則 (SRP)**: 每個模組、類別或函式都應該只有一個明確的職責。
- **高內聚，低耦合**: 相關的功能應該放在一起，模組之間的依賴應盡可能少。
- **可測試性**: 所有程式碼都應該易於進行單元測試和整合測試。依賴注入 (Dependency Injection) 是首選模式。
- **明確優於隱晦**: 程式碼應該清晰易懂，避免使用過於複雜或晦澀的語法。

## 3. Python 程式碼風格

本專案遵循 **PEP 8** 規範，並使用以下工具強制執行：

- **格式化**: `black`
- **排序 imports**: `isort`
- **靜態類型檢查**: `mypy`

### 3.1 命名規範

- **變數**: `snake_case` (e.g., `user_input`, `retrieved_chunks`)
- **函式**: `snake_case` (e.g., `create_github_issue`, `_private_helper_function`)
- **類別**: `PascalCase` (e.g., `CodeIndexer`, `StreamlitApp`)
- **常數**: `UPPER_SNAKE_CASE` (e.g., `SUPPORTED_EXTENSIONS`, `DEFAULT_MODEL`)
- **模組/套件**: `snake_case` (e.g., `src/core/indexer.py`)

### 3.2 類型提示 (Type Hinting)

- **強制性**: 所有函式簽名和類別屬性都必須有類型提示。
- **清晰性**: 使用 `typing` 模組提供的具體類型 (e.g., `List[str]`, `Dict[str, Any]`)。
- **Pydantic**: 在資料傳輸物件 (DTOs) 和 API 模型中，優先使用 `pydantic` 來定義結構和驗證。

```python
# Correct
from typing import List, Dict, Any
from pydantic import BaseModel

class CodeChunk(BaseModel):
    file_path: str
    content: str
    embedding: List[float]

def process_chunks(chunks: List[CodeChunk]) -> Dict[str, Any]:
    # ...
    pass
```

### 3.3 Docstrings

- **格式**: 遵循 **Google Style** Docstrings。
- **內容**: 必須包含 `Args`, `Returns`, 和 `Raises` (如果適用)。
- **範例**:

```python
def retrieve_relevant_code(query: str, top_k: int = 5) -> List[str]:
    """Retrieves relevant code snippets based on a natural language query.

    Args:
        query: The natural language query from the user.
        top_k: The number of relevant snippets to return.

    Returns:
        A list of code snippets that are most relevant to the query.
    """
    # ...
    pass
```

## 4. AI 代理程式與 LLM 互動風格

### 4.1 提示工程 (Prompt Engineering)

- **角色扮演 (Role-Playing)**: 在提示的開頭明確指定 LLM 的角色 (e.g., "You are an expert Python developer...").
- **結構化輸出**: 要求 LLM 以 JSON 或其他結構化格式回應，並提供 Pydantic 模型或 JSON Schema 作為參考。
- **上下文提供**: 將檢索到的相關資訊 (e.g., code snippets) 放在提示的特定區塊中，並用標記符 (e.g., `--- Context ---`) 包圍。
- **連鎖思考 (Chain-of-Thought)**: 對於複雜任務，要求 LLM "think step-by-step" 並將其推理過程包含在輸出中。

### 4.2 工具 (Tools) 設計

- **原子性**: 每個工具都應該執行一個單一、明確的操作 (e.g., `read_file`, `create_issue`)。
- **描述性名稱與文檔**: 工具的名稱和描述 (docstring) 必須清晰，以便 LLM 能夠理解其功能和參數。
- **錯誤處理**: 工具必須能夠處理預期的錯誤並回傳有意義的錯誤訊息。

## 5. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
