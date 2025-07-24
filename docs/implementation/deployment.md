# Deployment Guide

## 1. 概述

本文件描述了將 `Codex-Scribe` 專案部署到生產環境的策略和流程。它涵蓋了基礎設施、CI/CD 管道和部署工作流程。

**目標讀者**: 開發者、維運 (DevOps) 工程師。

## 2. 部署策略

本專案採用基於容器化的持續部署策略。所有服務（API 伺服器、索引器）都將被打包成 Docker 映像檔，並在雲端平台上運行。

- **雲端平台**: 建議使用 AWS、Google Cloud 或 Microsoft Azure。以下範例將以 AWS 為主。
- **容器化**: Docker
- **CI/CD**: GitHub Actions

## 3. 基礎設施架構 (AWS)

```mermaid
graph TD
    subgraph GitHub
        A[GitHub Repository] -- Push to main/develop --> B(GitHub Actions CI/CD)
    end

    subgraph AWS Cloud
        subgraph VPC
            C[API Gateway] --> D{Elastic Load Balancer};
            D --> E[ECS Fargate<br>(API Service)];
            B -- Deploy --> E;
            B -- Build & Push --> F[ECR<br>(Docker Image Registry)];
            E -- Pull Image --> F;
            
            G[EventBridge<br>(Scheduled Rule)] --> H[Lambda Function<br>(Trigger Indexing)];
            B -- Deploy --> H;
            H --> I[ECS Task<br>(Indexing Service)];
            I -- Pull Image --> F;

            E --> J[(Database<br>RDS/Managed DB)];
            I --> J;
        end
    end

    style F fill:#f9f, stroke:#333
    style J fill:#cde, stroke:#333
```

**組件說明**:

- **Amazon ECR (Elastic Container Registry)**: 用於存儲我們服務的 Docker 映像檔。
- **Amazon ECS (Elastic Container Service) with Fargate**:
    - **API 服務**: 作為一個常駐服務運行，處理來自 API Gateway 的實時請求。Fargate 提供了無伺服器的容器運行環境。
    - **索引服務**: 作為一個計劃性任務 (Scheduled Task) 運行，由 EventBridge 觸發，執行離線索引流程。
- **Amazon Lambda**: 一個輕量級的 Lambda 函式，用於接收來自 EventBridge 的事件並觸發 ECS 索引任務。
- **API Gateway**: 作為我們 API 的入口，處理路由、認證和速率限制。
- **EventBridge**: 用於設置定時規則（例如，每天凌晨 2 點）來觸發索引流程。
- **數據庫**:
    - **向量數據庫**: 對於生產環境，建議使用託管的向量數據庫服務，或者在 EC2/RDS 上自行管理 ChromaDB/Postgres+pgvector。
    - **圖形資料庫**: 使用託管的 Neo4j AuraDB 或在 EC2 上自行管理。

## 4. CI/CD 工作流程

我們將使用 GitHub Actions 建立兩個主要的工作流程。

### 4.1 `ci.yml` (持續整合)

- **觸發器**: 對 `develop` 分支的 `pull_request`。
- **工作**:
    1.  **Lint & Test**: 運行代碼質量檢查和所有層次的測試（單元、整合）。
    2.  **Build Docker Image**: 檢查 Dockerfile 是否能成功構建映像檔。
- **目的**: 確保合併到 `develop` 的程式碼是高質量的。

### 4.2 `cd.yml` (持續部署)

- **觸發器**: 對 `main` 分支的 `push`。
- **工作**:
    1.  **Configure AWS Credentials**: 使用 GitHub Secrets 安全地配置 AWS 訪問金鑰。
    2.  **Login to ECR**: 登錄到 Amazon ECR。
    3.  **Build and Push Docker Image**:
        - 構建 API 服務和索引服務的 Docker 映像檔。
        - 為映像檔打上 Git commit SHA 和 `latest` 標籤。
        - 將映像檔推送到 ECR。
    4.  **Deploy to ECS**:
        - 更新 ECS 服務定義，指向新的 Docker 映像檔版本。
        - 觸發 ECS 服務的滾動更新 (rolling update)。
    5.  **Deploy Lambda Function**: 將索引觸發器的 Lambda 函式打包並部署。

## 5. Dockerfile 範例

專案根目錄下應包含一個 `Dockerfile`。

```dockerfile
# Dockerfile

# 1. 使用官方 Python 映像檔作為基礎
FROM python:3.12-slim

# 2. 設置工作目錄
WORKDIR /app

# 3. 安裝 Poetry
RUN pip install poetry

# 4. 複製依賴管理文件
COPY poetry.lock pyproject.toml ./

# 5. 安裝依賴 (不包含開發依賴，並創建虛擬環境)
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# 6. 複製專案源碼
COPY src ./src
COPY scripts ./scripts

# 7. 開放端口 (如果適用)
EXPOSE 8000

# 8. 預設啟動命令 (用於 API 服務)
CMD ["uvicorn", "src.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
