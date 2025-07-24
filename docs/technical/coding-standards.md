# Coding Standards

## 1. 概述

本文件詳細定義了 `Codex-Scribe` 專案的程式碼規範和 Linting 配置。這些標準旨在確保程式碼的高度一致性、可讀性和可維護性。本文件是對根目錄下 `component-style-guide.md` 的具體化和技術實現。

**目標讀者**: 所有開發者。

## 2. 核心工具與配置

我們使用一系列工具來自動化地強制執行程式碼標準。所有配置都定義在 `pyproject.toml` 文件中。

### 2.1 Black - 無妥協的程式碼格式化工具

- **目的**: 統一所有 Python 程式碼的格式，結束關於風格的無謂爭論。
- **配置 (`pyproject.toml`)**:
    ```toml
    [tool.black]
    line-length = 88
    target-version = ['py312']
    ```
- **用法**:
    - **檢查格式**: `poetry run black --check .`
    - **自動格式化**: `poetry run black .`

### 2.2 isort - 導入語句排序工具

- **目的**: 自動排序和格式化 `import` 語句，使其清晰、一致。
- **配置 (`pyproject.toml`)**:
    ```toml
    [tool.isort]
    profile = "black"
    line_length = 88
    multi_line_output = 3
    ```
- **用法**:
    - **檢查格式**: `poetry run isort --check .`
    - **自動格式化**: `poetry run isort .`

### 2.3 mypy - 靜態類型檢查工具

- **目的**: 在運行前捕獲類型相關的錯誤，提高程式碼的健壯性。
- **配置 (`pyproject.toml`)**:
    ```toml
    [tool.mypy]
    python_version = "3.12"
    warn_return_any = true
    warn_unused_configs = true
    ignore_missing_imports = true # 某些庫可能沒有類型存根
    strict = true # 啟用所有嚴格檢查選項
    ```
- **用法**:
    - `poetry run mypy src`

## 3. 程式碼規範細則

### 3.1 錯誤處理

- **使用自定義異常**: 在 `src/domain/exceptions.py` 中定義業務相關的自定義異常（如 `AnalysisError`, `IndexingError`），而不是直接使用通用的 `Exception`。
- **避免空的 `except`**: 絕不使用 `except:`。至少要捕獲 `except Exception:` 並記錄日誌。
- **清晰的錯誤訊息**: 異常訊息應該清晰地描述問題所在。

### 3.2 日誌記錄

- **使用標準 `logging` 模組**: 不要使用 `print()` 語句進行日誌記錄。
- **在函式/類別開頭獲取 logger**: `logger = logging.getLogger(__name__)`。
- **記錄有用的上下文**: 在日誌中包含相關的變數值，如 `task_id`, `file_path` 等。

```python
import logging

logger = logging.getLogger(__name__)

def process_file(file_path: str):
    logger.info("Starting to process file: %s", file_path)
    try:
        # ... some logic ...
        logger.info("Successfully processed file: %s", file_path)
    except Exception as e:
        logger.error("Failed to process file: %s. Error: %s", file_path, e, exc_info=True)
        raise
```

### 3.3 Clean Architecture 實踐

- **依賴方向**: 依賴關係必須始終指向內部。`infrastructure` 和 `presentation` 層可以依賴 `application` 和 `domain` 層，但反之則不行。
- **數據傳輸物件 (DTOs)**: 在層與層之間傳遞數據時，使用 Pydantic 模型作為 DTOs，而不是直接傳遞數據庫模型或框架特定的物件。
- **介面隔離**: `application` 層應定義抽象的存儲庫 (Repository) 介面，而 `infrastructure` 層則提供具體的實現。

## 4. Pre-commit Hooks

為了在提交程式碼之前自動運行這些檢查，我們將使用 `pre-commit` 工具。

- **配置文件**: `.pre-commit-config.yaml`
- **配置範例**:
    ```yaml
    repos:
    -   repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.6.0
        hooks:
        -   id: trailing-whitespace
        -   id: end-of-file-fixer
        -   id: check-yaml
        -   id: check-added-large-files
    -   repo: https://github.com/psf/black
        rev: 24.4.2
        hooks:
        -   id: black
    -   repo: https://github.com/pycqa/isort
        rev: 5.13.2
        hooks:
        -   id: isort
    -   repo: https://github.com/pycqa/mypy
        rev: v1.10.0
        hooks:
        -   id: mypy
    ```
- **安裝**:
    - `poetry add pre-commit --group dev`
    - `poetry run pre-commit install`

之後，每次 `git commit` 時，這些檢查都會自動運行。

## 5. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
