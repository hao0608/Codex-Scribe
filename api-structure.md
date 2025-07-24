# API Structure Guide

## 1. 概述

本文件定義了 `Codex-Scribe` 專案中所有 API 的設計規範和結構。統一的 API 風格有助於提高開發效率、降低整合成本並增強系統的健壯性。本專案將採用 **RESTful** 設計原則。

**目標讀者**: 所有參與此專案的開發者和 AI 代理程式。

## 2. 設計原則

- **資源導向**: API 應該圍繞資源（如 `issues`, `code_snippets`）進行設計。
- **使用標準 HTTP 方法**:
    - `GET`: 讀取資源。
    - `POST`: 建立新資源。
    - `PUT`: 完整更新現有資源。
    - `PATCH`: 部分更新現有資源。
    - `DELETE`: 刪除資源。
- **無狀態 (Stateless)**: 伺服器不應該保存客戶端的狀態。每個請求都應包含所有必要的資訊。
- **使用 JSON**: 所有請求主體 (Request Body) 和回應主體 (Response Body) 都應使用 JSON 格式。

## 3. URL 結構

- **使用名詞複數**: 端點應使用名詞的複數形式來表示資源集合 (e.g., `/issues`, `/analyses`)。
- **層級關係**: 使用 `/` 來表示資源之間的層級關係 (e.g., `/repositories/{repo_id}/issues`)。
- **路徑參數**: 使用 `{}` 來表示唯一的資源標識符 (e.g., `/issues/{issue_id}`)。
- **查詢參數**: 用於過濾、排序和分頁 (e.g., `/issues?status=open&sort=created_at`)。
- **版本控制**: 將 API 版本包含在 URL 路徑中 (e.g., `/api/v1/issues`)。

## 4. 請求 (Request)

### 4.1 標頭 (Headers)

- `Content-Type`: 對於有請求主體的請求（`POST`, `PUT`, `PATCH`），必須設置為 `application/json`。
- `Authorization`: 對於需要認證的端點，使用 `Bearer` token (e.g., `Authorization: Bearer <YOUR_TOKEN>`)。

### 4.2 請求主體 (Body)

- 使用 `snake_case` 命名 JSON 欄位。
- 使用 Pydantic 進行嚴格的數據驗證。

```json
// POST /api/v1/analyses
{
  "source": "github_comment",
  "content": "The login page is broken on mobile.",
  "metadata": {
    "repository_url": "https://github.com/hao0608/Codex-Scribe",
    "comment_id": "c_12345"
  }
}
```

## 5. 回應 (Response)

### 5.1 狀態碼 (Status Codes)

- **2xx (成功)**:
    - `200 OK`: 請求成功（用於 `GET`, `PUT`, `PATCH`）。
    - `201 Created`: 資源成功建立（用於 `POST`）。
    - `204 No Content`: 請求成功但無內容返回（用於 `DELETE`）。
- **4xx (客戶端錯誤)**:
    - `400 Bad Request`: 請求無效（如格式錯誤、缺少參數）。
    - `401 Unauthorized`: 未經授權。
    - `403 Forbidden`: 禁止訪問。
    - `404 Not Found`: 資源不存在。
- **5xx (伺服器錯誤)**:
    - `500 Internal Server Error`: 伺服器內部發生未知錯誤。

### 5.2 回應主體 (Body)

- **統一格式**: 所有回應都應包含在一個 `data` 物件中，並可能包含 `metadata` 或 `error` 物件。
- **使用 `snake_case`**: JSON 欄位名稱。

**成功回應範例 (`200 OK`)**:
```json
{
  "data": {
    "issue_id": 5,
    "title": "Bug: Login page broken on mobile",
    "status": "open",
    "created_at": "2025-07-24T11:15:00Z"
  },
  "metadata": {
    "request_id": "uuid-goes-here"
  }
}
```

**錯誤回應範例 (`400 Bad Request`)**:
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Field 'content' is required.",
    "details": [
      {
        "field": "content",
        "issue": "missing"
      }
    ]
  },
  "metadata": {
    "request_id": "uuid-goes-here"
  }
}
```

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
