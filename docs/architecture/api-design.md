# API Design Specification

## 1. 概述

本文件提供了 `Codex-Scribe` 專案 API 的詳細設計規範。它基於根目錄下的 `api-structure.md` 文件中定義的 RESTful 原則，並提供了具體的端點 (Endpoint) 定義、請求/回應模型和錯誤處理機制。

**目標讀者**: 前後端開發者、API 消費者。

## 2. 通用規範

- **基礎 URL**: `https://api.codex-scribe.app/api/v1`
- **認證**: 所有端點都需要 `Authorization: Bearer <API_KEY>` 標頭。
- **數據格式**: 所有請求和回應主體均為 `application/json`。
- **命名慣例**: JSON 欄位和 URL 參數均使用 `snake_case`。

## 3. 核心資源與端點

### 3.1 資源: `Analysis`

代表一次對文本或程式碼的分析任務。

#### `POST /analyses`

- **描述**: 觸發一次新的分析任務，並可選擇性地根據分析結果建立一個 GitHub issue。
- **請求模型 (`AnalysisRequest`)**:
    ```json
    {
      "content": "string", // The user feedback or text to be analyzed
      "source_type": "string", // e.g., "github_comment", "slack_message", "manual_input"
      "repository_url": "string", // Target repository for analysis
      "create_issue": "boolean", // Default: false. If true, create a GitHub issue
      "metadata": { // Optional metadata
        "comment_id": "string",
        "user": "string"
      }
    }
    ```
- **成功回應 (`202 Accepted`)**:
    - 由於分析可能是異步的，伺服器立即返回 `202`，表示已接受請求。
    - 回應主體包含一個任務 ID，可用於後續查詢狀態。
    ```json
    {
      "data": {
        "task_id": "ts_a7b2c8f3",
        "status": "pending",
        "message": "Analysis task has been accepted and is being processed."
      }
    }
    ```

#### `GET /analyses/{task_id}`

- **描述**: 查詢特定分析任務的狀態和結果。
- **成功回應 (`200 OK`)**:
    ```json
    {
      "data": {
        "task_id": "ts_a7b2c8f3",
        "status": "completed", // or "pending", "failed"
        "result": {
          "summary": "The user reported a login issue on mobile devices.",
          "sentiment": "negative",
          "extracted_entities": ["login", "mobile"],
          "github_issue": { // Present if create_issue was true and successful
            "issue_url": "https://github.com/hao0608/Codex-Scribe/issues/15",
            "issue_number": 15
          }
        }
      }
    }
    ```

### 3.2 資源: `Repository`

代表被索引和分析的程式碼庫。

#### `POST /repositories/index`

- **描述**: 觸發對指定程式碼庫的離線索引任務。
- **請求模型 (`IndexRequest`)**:
    ```json
    {
      "repository_url": "string"
    }
    ```
- **成功回應 (`202 Accepted`)**:
    ```json
    {
      "data": {
        "task_id": "idx_b8c3d9a4",
        "status": "pending",
        "message": "Repository indexing task has been scheduled."
      }
    }
    ```

## 4. 錯誤處理

系統使用標準的 HTTP 狀態碼，並在回應主體中提供結構化的錯誤訊息。

- **錯誤回應模型 (`ErrorResponse`)**:
    ```json
    {
      "error": {
        "code": "string", // e.g., "invalid_parameter", "authentication_failed"
        "message": "string", // A human-readable error message
        "target": "string", // Optional: the field that caused the error
        "details": [ // Optional: more detailed error info
          {
            "code": "missing_field",
            "target": "content",
            "message": "The 'content' field is required for analysis."
          }
        ]
      }
    }
    ```

**範例 (`400 Bad Request`)**:
```json
// Request: POST /analyses with missing "content" field
{
  "error": {
    "code": "invalid_request",
    "message": "The request body is invalid.",
    "details": [
      {
        "code": "missing_field",
        "target": "content",
        "message": "The 'content' field is required for analysis."
      }
    ]
  }
}
```

**範例 (`401 Unauthorized`)**:
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication failed. Please provide a valid API key."
  }
}
```

## 5. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
