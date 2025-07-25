# Phase 1: MVP - Code Question Answering Bot

## 1. 概述

本文件詳細描述了 `Codex-Scribe` 專案第一階段（MVP）的開發計劃。此階段的目標是建立一個最小可行性產品：一個能夠對指定程式碼庫進行自然語言問答的機器人。

**目標**: 證明 AI 理解程式碼庫的可行性，並為後續階段建立堅實的技術基礎。

## 2. 功能與範圍

### 2.1 核心功能

- **程式碼索引**: 能夠遞迴掃描本地的 GitHub 專案副本，並為程式碼文件建立向量索引。
- **語義搜索**: 能夠根據自然語言問題，在索引中搜索最相關的程式碼片段。
- **問答生成 (RAG)**: 結合問題和檢索到的程式碼片段，利用 LLM 生成準確的回答。
- **用戶介面**: 提供一個簡單的 Web UI（使用 Streamlit）來進行問答互動。

### 2.2 範圍限制 (Out of Scope)

- **自動化觸發**: 本階段不包含 GitHub Webhook 或自動化流程。
- **知識圖譜**: 不包含 AST 解析或圖形資料庫的整合。
- **自動問題建立**: 不會自動在 GitHub 上建立 issue。
- **多代理程式協作**: 僅使用單一的 RAG 鏈。

## 3. 技術棧

- **語言**: Python 3.12+
- **AI 框架**: LangChain
- **LLM**: OpenAI GPT-4o (或同等級模型)
- **嵌入模型**: OpenAI `text-embedding-3-large`
- **向量資料庫**: ChromaDB (本地持久化)
- **UI 框架**: Streamlit
- **開發工具**: Poetry, Black, isort, mypy, pytest

## 4. 開發里程碑與任務分解

### 里程碑 1: 專案設置與環境配置 (`feature/phase-1-setup`)

- [x] 初始化 Poetry 專案。
- [x] 更新 `pyproject.toml` 和 `requirements.txt`，加入所有必要依賴。
- [x] 建立 `src` 目錄結構，遵循 Clean Architecture 原則。
- [x] 配置 `.env` 文件，管理 API keys。
- [x] 設置 `black`, `isort`, `mypy` 等代碼質量工具。

### 里程碑 2: 程式碼索引器 (`feature/code-indexer`)

- [x] **檔案加載器**: 實作一個能夠遞迴讀取指定目錄下程式碼文件的模組 (`file_processor.py`)。
    - 支持的擴展名: `.py`, `.md`, `.js`, `.ts` 等。
- [x] **文本分割器**: 使用 `RecursiveCharacterTextSplitter`，並針對程式碼進行優化，使其盡可能按函數或類別邊界分割。
- [x] **索引腳本 (`scripts/index_repository.py`)**:
    - 接收一個本地路徑作為參數。
    - 調用檔案加載器和文本分割器。
    - 使用嵌入模型生成向量。
    - 將程式碼塊和向量存入本地 ChromaDB。

### 里程碑 3: RAG 檢索與生成 (`feature/rag-retriever`)

- [x] **檢索器模組 (`core/retriever.py`)**:
    - 連接到 ChromaDB。
    - 接收一個查詢字串，將其轉換為向量。
    - 執行相似性搜索，返回 `top_k` 個最相關的程式碼塊。
- [x] **LLM 客戶端 (`core/llm_client.py`)**:
    - 封裝與 OpenAI API 的互動。
- [x] **RAG 鏈**:
    - 建立一個 LangChain 表達式語言 (LCEL) 鏈。
    - 鏈的流程: `(Query -> Retriever -> Format Docs) | PromptTemplate | LLM | OutputParser`

### 里程碑 4: Streamlit 用戶介面 (`feature/streamlit-ui`)

- [x] **UI 佈局 (`ui/streamlit_app.py`)**:
    - 標題和專案描述。
    - 一個文本輸入框用於提問。
    - 一個按鈕用於提交問題。
    - 一個區域用於顯示 LLM 的回答。
    - (可選) 一個擴展區域用於顯示檢索到的原始程式碼片段。
- [x] **後端邏輯**:
    - 當用戶提交問題時，調用 RAG 鏈。
    - 將結果流式傳輸 (stream) 到前端介面，以改善用戶體驗。

## 5. 驗收標準

### 5.1 功能性測試

- [x] **索引腳本**: 能夠成功索引專案的 `src/` 和 `docs/` 目錄。
- [x] **斷點續傳**: 重複執行索引命令，能夠自動跳過已索引的內容。
- [x] **目錄過濾**: `--include-dirs` 參數能夠正確地只索引指定目錄。
- [x] **UI 啟動**: Streamlit 應用能夠成功啟動並顯示介面。
- [x] **問答功能**: 系統能夠基於 `src/` 和 `docs/` 的內容，對相關問題給出合理的中文回答。
- [x] **程式碼檢索**: 當問題與程式碼相關時，回答中應包含相關的程式碼片段。

### 5.2 性能基準

- [ ] **索引時間**: 記錄索引 `src/` 和 `docs/` 目錄所需的總時間，作為未來優化的基準。
- [ ] **回應時間**: 記錄從提問到收到完整回答的平均時間（測試 5 次）。

### 5.3 程式碼品質

- [x] **靜態分析**: 所有程式碼均通過 `mypy`, `ruff`, `black`, `isort` 的檢查。
- [x] **提交歷史**: Git 提交歷史清晰，遵循 Conventional Commits 規範。
- [ ] **錯誤處理**: 核心流程（如索引、問答）有基本的 `try...except` 錯誤處理機制。

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
| 2025-07-25 | 1.1  | 更新所有已完成的里程碑狀態 | Cline  |
| 2025-07-25 | 1.2  | 修訂驗收標準為可執行的測試項目 | Cline  |
