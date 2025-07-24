# Setup and Installation Guide

## 1. 概述

本文件提供了在本地開發環境中設置和運行 `Codex-Scribe` 專案的完整指南。

**目標讀者**: 新加入專案的開發者。

## 2. 先決條件

在開始之前，請確保您的系統已安裝以下軟體：

- **Python**: 版本 3.12 或更高。
- **Git**: 用於版本控制。
- **Poetry**: 用於 Python 依賴管理。
- **Docker** 和 **Docker Compose**: 用於運行 Neo4j 等外部服務（階段三需要）。

## 3. 安裝步驟

### 步驟 1: 克隆儲存庫

首先，將專案程式碼克隆到您的本地機器：

```bash
git clone https://github.com/hao0608/Codex-Scribe.git
cd Codex-Scribe
```

### 步驟 2: 安裝依賴

本專案使用 Poetry 管理依賴。運行以下命令來安裝所有必需的套件：

```bash
poetry install
```
這將會創建一個虛擬環境並安裝 `pyproject.toml` 中定義的所有依賴。

### 步驟 3: 配置環境變數

系統需要 API 金鑰來與外部服務（如 OpenAI）互動。

1.  複製範例環境文件：
    ```bash
    cp .env.example .env
    ```
    *如果 `.env.example` 不存在，請手動創建 `.env` 文件。*

2.  編輯 `.env` 文件，並填入您的 API 金鑰：
    ```dotenv
    # .env
    # OpenAI API Key
    OPENAI_API_KEY="sk-..."

    # GitHub Personal Access Token (with repo and issue permissions)
    GITHUB_PAT="ghp_..."
    ```

### 步驟 4: 激活虛擬環境

要運行專案中的腳本或應用，您需要先激活由 Poetry 創建的虛擬環境：

```bash
poetry shell
```
成功激活後，您的命令提示符應該會顯示虛擬環境的名稱。

## 4. 運行應用

### 4.1 運行索引腳本 (階段一)

在開始問答之前，您需要先對目標程式碼庫進行索引。

```bash
# 確保您在 poetry shell 中
python scripts/index_repository.py --path /path/to/your/target/repository
```
*注意：第一次運行時，這可能需要幾分鐘時間，具體取決於程式碼庫的大小。*

### 4.2 運行 Streamlit UI (階段一)

索引完成後，您可以啟動問答介面：

```bash
streamlit run src/presentation/ui/streamlit_app.py
```
應用程式將在您的本地瀏覽器中打開，通常地址為 `http://localhost:8501`。

### 4.3 運行 FastAPI 伺服器 (階段二)

對於階段二的 API 功能，您需要運行 Uvicorn 伺服器：

```bash
uvicorn src.presentation.api.main:app --reload
```
API 服務將在 `http://localhost:8000` 上可用。您可以通過 `http://localhost:8000/docs` 訪問自動生成的 Swagger UI。

### 4.4 運行 Neo4j (階段三)

對於階段三的知識圖譜功能，您需要使用 Docker Compose 啟動 Neo4j 服務：

```bash
docker-compose up -d neo4j
```
Neo4j 瀏覽器將在 `http://localhost:7474` 上可用。

## 5. 疑難排解

- **`poetry install` 失敗**:
    - 確保您的 Python 版本符合 `pyproject.toml` 中的要求 (`>=3.12`)。
    - 嘗試更新 Poetry 到最新版本: `poetry self update`。
- **環境變數未加載**:
    - 確保您的 `.env` 文件位於專案的根目錄。
    - 確保您使用了 `python-dotenv` 函式庫來加載變數。
- **Streamlit/FastAPI 無法啟動**:
    - 確保您已經使用 `poetry shell` 激活了虛擬環境。

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
