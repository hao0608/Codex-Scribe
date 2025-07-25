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

- [ ] 初始化 Poetry 專案。
- [ ] 更新 `pyproject.toml` 和 `requirements.txt`，加入所有必要依賴。
- [ ] 建立 `src` 目錄結構，遵循 Clean Architecture 原則。
- [ ] 配置 `.env` 文件，管理 API keys。
- [ ] 設置 `black`, `isort`, `mypy` 等代碼質量工具。

### 里程碑 2: 程式碼索引器 (`feature/code-indexer`)

- [ ] **檔案加載器**: 實作一個能夠遞迴讀取指定目錄下程式碼文件的模組 (`file_processor.py`)。
    - 支持的擴展名: `.py`, `.md`, `.js`, `.ts` 等。
- [ ] **文本分割器**: 使用 `RecursiveCharacterTextSplitter`，並針對程式碼進行優化，使其盡可能按函數或類別邊界分割。
- [ ] **索引腳本 (`scripts/index_repository.py`)**:
    - 接收一個本地路徑作為參數。
    - 調用檔案加載器和文本分割器。
    - 使用嵌入模型生成向量。
    - 將程式碼塊和向量存入本地 ChromaDB。

### 里程碑 3: RAG 檢索與生成 (`feature/rag-retriever`)

- [ ] **檢索器模組 (`core/retriever.py`)**:
    - 連接到 ChromaDB。
    - 接收一個查詢字串，將其轉換為向量。
    - 執行相似性搜索，返回 `top_k` 個最相關的程式碼塊。
- [ ] **LLM 客戶端 (`core/llm_client.py`)**:
    - 封裝與 OpenAI API 的互動。
- [ ] **RAG 鏈**:
    - 建立一個 LangChain 表達式語言 (LCEL) 鏈。
    - 鏈的流程: `(Query -> Retriever -> Format Docs) | PromptTemplate | LLM | OutputParser`

### 里程碑 4: Streamlit 用戶介面 (`feature/streamlit-ui`)

- [ ] **UI 佈局 (`ui/streamlit_app.py`)**:
    - 標題和專案描述。
    - 一個文本輸入框用於提問。
    - 一個按鈕用於提交問題。
    - 一個區域用於顯示 LLM 的回答。
    - (可選) 一個擴展區域用於顯示檢索到的原始程式碼片段。
- [ ] **後端邏輯**:
    - 當用戶提交問題時，調用 RAG 鏈。
    - 將結果流式傳輸 (stream) 到前端介面，以改善用戶體驗。

## 5. 驗收標準

- **功能性**:
    - [ ] 索引腳本能夠成功索引 `https://github.com/hao0608/Codex-Scribe` 專案本身。
    - [ ] 在 Streamlit UI 中提問 "What is the purpose of the Code Indexing Pipeline?"，系統應能給出基於 `system-overview.md` 的準確回答。
    - [ ] 提問關於 Python 程式碼的問題，系統能返回相關的程式碼片段並給出解釋。
- **性能**:
    - [ ] 中等規模專案（~100個文件）的索引時間應在 5 分鐘以內。
    - [ ] UI 中的問答響應時間應在 5 秒以內。
- **程式碼品質**:
    - [ ] 所有程式碼都遵循 `component-style-guide.md` 中的規範。
    - [ ] 主要模組都有對應的單元測試。
    - [ ] `mypy` 類型檢查通過率 100%。

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
