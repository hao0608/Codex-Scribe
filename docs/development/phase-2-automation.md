# Phase 2: Automation - GitHub Integration

## 1. 概述

本文件詳細描述了 `Codex-Scribe` 專案第二階段的開發計劃。在完成 MVP（程式碼問答機器人）後，此階段的目標是將系統與 GitHub 工作流程整合，實現從用戶回饋到建立 GitHub 問題草稿的半自動化流程。

**目標**: 提高開發效率，將 AI 的分析能力直接應用於專案管理工具中。

## 2. 功能與範圍

### 2.1 核心功能

- **GitHub API 整合**: 能夠通過 API 安全地認證並與指定的 GitHub 儲存庫互動。
- **結構化輸出**: 訓練 LLM 將其分析結果格式化為結構化的 JSON 物件，該物件對應 GitHub issue 的欄位（標題、內容、標籤）。
- **問題草稿建立**: 能夠根據 LLM 生成的 JSON 物件，在 GitHub 上自動建立一個帶有特定標籤（如 `ai-draft`, `needs-review`）的問題。
- **API 觸發器**: 建立一個 FastAPI 端點，可以接收外部請求（如來自內部表單的用戶回饋），並觸發整個分析和問題建立流程。

### 2.2 範圍限制 (Out of Scope)

- **Webhook 自動觸發**: 本階段暫不處理來自 GitHub 的實時 Webhook 事件。
- **複雜的 UI**: 僅提供 API 端點，不擴展現有的 Streamlit UI 功能。
- **自動解決問題**: 系統只負責建立問題草稿，不涉及後續的程式碼修改或 PR 提交。

## 3. 技術棧

- **Web 框架**: FastAPI (用於建立 API 端點)
- **伺服器**: Uvicorn
- **GitHub 客戶端**: PyGithub
- **數據驗證**: Pydantic (用於 API 模型和 LLM 結構化輸出)
- **其他**: 延續階段一的技術棧 (LangChain, OpenAI, ChromaDB)。

## 4. 開發里程碑與任務分解

### 里程碑 1: GitHub API 客戶端 (`feature/github-client`)

- [x] **認證模組**: 在 `src/infrastructure/github` 中建立一個模組，負責處理 GitHub 個人存取令牌 (PAT) 的安全讀取和管理。
- [x] **API 封裝**: 建立一個 `GitHubService` 類別，封裝常用的 API 操作，特別是 `create_issue`。
    - `create_issue(title: str, body: str, labels: List[str]) -> Issue`
- [x] **錯誤處理**: 確保客戶端能妥善處理 API 錯誤（如權限不足、速率限制）。
- [x] **單元測試**: 編寫測試用例來驗證 `GitHubService` 的功能（可使用 `unittest.mock` 來模擬 API 呼叫）。

### 里程碑 2: LLM 結構化輸出 (`feature/structured-output`)

- [x] **Pydantic 模型**: 在 `src/domain/entities` 中定義一個 `GitHubIssueDraft` Pydantic 模型，包含 `title`, `body`, `labels` 欄位。
- [x] **輸出解析器**: 使用 LangChain 的 `PydanticOutputParser` 來確保 LLM 的輸出嚴格符合 `GitHubIssueDraft` 模型。
- [x] **提示工程優化**:
    - 修改 RAG 鏈中的提示模板。
    - 明確指示 LLM 根據上下文分析，並以指定的 JSON 格式輸出結果。
    - 在提示中提供 JSON 格式的範例 (few-shot)。

### 里程碑 3: FastAPI 觸發器 (`feature/api-trigger`)

- [x] **安裝依賴**: 將 `fastapi` 和 `uvicorn` 添加到 `pyproject.toml`。
- [x] **建立 API 應用**: 在 `src/presentation/api` 中建立 `main.py`。
- [x] **定義請求模型**: 使用 Pydantic 建立一個 `AnalysisRequest` 模型，用於接收用戶回饋文本。
- [x] **建立端點 (`/api/v1/analyze-and-create-issue`)**:
    - 該端點接收一個 `AnalysisRequest`。
    - 調用現有的 RAG 鏈來處理文本，並生成結構化的 `GitHubIssueDraft`。
    - 調用 `GitHubService` 將草稿發佈到 GitHub。
    - 返回成功建立的 issue URL。

## 5. 驗收標準

- **功能性**:
    - [x] `GitHubService` 能夠成功在 `hao0608/Codex-Scribe` 儲存庫中建立一個測試 issue。
    - [x] 向 FastAPI 端點發送一段用戶回饋，系統能夠成功執行 RAG 分析，並在 GitHub 上建立一個格式正確、內容相關的問題草稿。
    - [x] 建立的問題應自動附帶 `ai-draft` 和 `needs-review` 標籤。
- **性能**:
    - [x] 從 API 請求到 GitHub issue 建立完成的總時間應在 15 秒以內。
- **程式碼品質**:
    - [x] 所有新程式碼都遵循專案的程式碼風格和設計原則。
    - [x] FastAPI 端點和 GitHub 客戶端都有充分的單元測試覆蓋。

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
| 2025-07-28 | 2.0  | 完成第二階段開發   | Cline  |
