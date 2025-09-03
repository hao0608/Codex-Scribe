# Multi-Repository API Specification

## 1. 概述

本文件定義了 `Codex-Scribe` 多儲存庫功能的完整 API 規範。包含儲存庫管理、查詢增強和相關的資料模型定義。

**目標讀者**: API 使用者、前端開發者、整合開發者

## 2. 基礎資料模型

### 2.1 RepositoryMetadata

```python
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class RepositoryStatus(str, Enum):
    INDEXING = "indexing"
    INDEXED = "indexed"
    ERROR = "error"
    DELETED = "deleted"

class RepositoryMetadata(BaseModel):
    name: str  # Format: "owner/repo-name"
    display_name: str
    url: HttpUrl
    indexed_at: Optional[datetime] = None
    file_count: int = 0
    chunk_count: int = 0
    node_count: int = 0
    edge_count: int = 0
    status: RepositoryStatus = RepositoryStatus.INDEXING
    include_dirs: List[str] = []
    exclude_patterns: List[str] = []
    error_message: Optional[str] = None
```

### 2.2 RepositoryIndexRequest

```python
class RepositoryIndexRequest(BaseModel):
    url: HttpUrl
    include_dirs: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    force_reindex: bool = False
```

### 2.3 QueryRequest

```python
class QueryScope(str, Enum):
    SINGLE = "single"      # 查詢單一儲存庫
    MULTIPLE = "multiple"  # 查詢指定儲存庫列表
    ALL = "all"           # 查詢所有儲存庫

class SearchType(str, Enum):
    VECTOR = "vector"      # 純向量搜索
    GRAPH = "graph"        # 純圖形查詢
    HYBRID = "hybrid"      # 混合搜索

class MultiRepoQueryRequest(BaseModel):
    query: str
    search_type: SearchType = SearchType.HYBRID
    scope: QueryScope = QueryScope.ALL
    repositories: Optional[List[str]] = None  # 當 scope = MULTIPLE 時必填
    top_k: int = 5
    include_metadata: bool = True
```

### 2.4 QueryResponse

```python
class CodeResult(BaseModel):
    content: str
    file_path: str
    repository_name: str
    chunk_id: str
    similarity_score: Optional[float] = None
    metadata: dict = {}

class GraphResult(BaseModel):
    query_type: str  # "callers", "methods", "dependencies", etc.
    results: List[dict]
    repository_name: str

class MultiRepoQueryResponse(BaseModel):
    query: str
    total_results: int
    processing_time_ms: int
    repositories_searched: List[str]
    code_results: List[CodeResult] = []
    graph_results: List[GraphResult] = []
    answer: Optional[str] = None  # LLM 生成的綜合回答
```

## 3. Repository Management APIs

### 3.1 List Repositories

**Endpoint**: `GET /api/v1/repositories`

**Response**:
```python
class RepositoryListResponse(BaseModel):
    repositories: List[RepositoryMetadata]
    total_count: int
```

**HTTP Status Codes**:
- `200 OK`: 成功返回儲存庫列表

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/repositories"
```

### 3.2 Get Repository Details

**Endpoint**: `GET /api/v1/repositories/{repository_name}`

**Parameters**:
- `repository_name`: Path parameter, format "owner/repo-name"

**Response**: `RepositoryMetadata`

**HTTP Status Codes**:
- `200 OK`: 成功返回儲存庫詳情
- `404 Not Found`: 儲存庫不存在

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/repositories/user/my-repo"
```

### 3.3 Index Repository

**Endpoint**: `POST /api/v1/repositories`

**Request Body**: `RepositoryIndexRequest`

**Response**:
```python
class RepositoryIndexResponse(BaseModel):
    repository_name: str
    status: str
    message: str
    task_id: Optional[str] = None  # For async indexing
```

**HTTP Status Codes**:
- `201 Created`: 索引任務已開始
- `400 Bad Request`: 請求參數錯誤
- `409 Conflict`: 儲存庫已存在且 force_reindex=false

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/repositories" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/my-repo",
    "include_dirs": ["src/", "docs/"],
    "exclude_patterns": ["*.pyc", "__pycache__/"]
  }'
```

### 3.4 Delete Repository

**Endpoint**: `DELETE /api/v1/repositories/{repository_name}`

**Parameters**:
- `repository_name`: Path parameter, format "owner/repo-name"

**Response**:
```python
class RepositoryDeleteResponse(BaseModel):
    repository_name: str
    deleted: bool
    message: str
```

**HTTP Status Codes**:
- `200 OK`: 儲存庫已成功刪除
- `404 Not Found`: 儲存庫不存在

### 3.5 Reindex Repository

**Endpoint**: `POST /api/v1/repositories/{repository_name}/reindex`

**Parameters**:
- `repository_name`: Path parameter, format "owner/repo-name"

**Request Body**:
```python
class ReindexRequest(BaseModel):
    include_dirs: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
```

**Response**: `RepositoryIndexResponse`

**HTTP Status Codes**:
- `202 Accepted`: 重新索引任務已開始
- `404 Not Found`: 儲存庫不存在

## 4. Query APIs

### 4.1 Single Repository Query

**Endpoint**: `POST /api/v1/repositories/{repository_name}/query`

**Parameters**:
- `repository_name`: Path parameter, format "owner/repo-name"

**Request Body**:
```python
class SingleRepoQueryRequest(BaseModel):
    query: str
    search_type: SearchType = SearchType.HYBRID
    top_k: int = 5
    include_metadata: bool = True
```

**Response**: `MultiRepoQueryResponse`

**HTTP Status Codes**:
- `200 OK`: 查詢成功
- `404 Not Found`: 儲存庫不存在

### 4.2 Multi-Repository Query

**Endpoint**: `POST /api/v1/query`

**Request Body**: `MultiRepoQueryRequest`

**Response**: `MultiRepoQueryResponse`

**HTTP Status Codes**:
- `200 OK`: 查詢成功
- `400 Bad Request`: 查詢參數錯誤

### 4.3 Repository Search

**Endpoint**: `GET /api/v1/repositories/search`

**Query Parameters**:
- `q`: 搜索關鍵字
- `status`: 篩選狀態 (optional)
- `limit`: 結果數量限制 (default: 20)

**Response**:
```python
class RepositorySearchResponse(BaseModel):
    query: str
    repositories: List[RepositoryMetadata]
    total_count: int
```

## 5. Analytics and Monitoring APIs

### 5.1 Repository Statistics

**Endpoint**: `GET /api/v1/repositories/{repository_name}/stats`

**Response**:
```python
class RepositoryStats(BaseModel):
    repository_name: str
    file_types: dict  # {"py": 50, "md": 10, ...}
    total_lines_of_code: int
    average_chunk_size: float
    most_connected_files: List[str]
    indexing_duration_seconds: float
    last_query_at: Optional[datetime]
    query_count_24h: int
```

### 5.2 System Health

**Endpoint**: `GET /api/v1/health`

**Response**:
```python
class SystemHealth(BaseModel):
    status: str  # "healthy", "warning", "error"
    timestamp: datetime
    repositories_count: int
    active_indexing_tasks: int
    database_connections: dict
    disk_usage: dict
    memory_usage: dict
```

## 6. Webhooks and Events

### 6.1 Repository Events

**Endpoint**: `POST /api/v1/webhooks/repository-events`

**Event Types**:
```python
class RepositoryEventType(str, Enum):
    INDEXING_STARTED = "indexing_started"
    INDEXING_COMPLETED = "indexing_completed"
    INDEXING_FAILED = "indexing_failed"
    REPOSITORY_DELETED = "repository_deleted"

class RepositoryEvent(BaseModel):
    event_type: RepositoryEventType
    repository_name: str
    timestamp: datetime
    data: dict = {}
```

## 7. Error Handling

### 7.1 Standard Error Response

```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime
    request_id: str
```

### 7.2 Common Error Codes

- `REPOSITORY_NOT_FOUND`: 儲存庫不存在
- `REPOSITORY_ALREADY_EXISTS`: 儲存庫已存在
- `INDEXING_IN_PROGRESS`: 儲存庫正在索引中
- `INVALID_REPOSITORY_URL`: 無效的儲存庫 URL
- `INSUFFICIENT_PERMISSIONS`: 權限不足
- `STORAGE_LIMIT_EXCEEDED`: 儲存空間不足
- `QUERY_TIMEOUT`: 查詢超時

## 8. Rate Limiting

### 8.1 限制規則

- **Repository Management**: 10 requests/minute per IP
- **Indexing**: 5 concurrent indexing tasks per user
- **Queries**: 100 requests/minute per API key
- **Bulk Operations**: 1 request/minute per user

### 8.2 Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

## 9. Authentication & Authorization

### 9.1 API Key Authentication

```
Authorization: Bearer your-api-key
```

### 9.2 Repository-level Permissions

```python
class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class RepositoryPermission(BaseModel):
    repository_name: str
    permission: Permission
```

## 10. 版本控制與相容性

### 10.1 API 版本

- **Current Version**: v1
- **Supported Versions**: v1
- **Deprecation Policy**: 6個月預告期

### 10.2 向後相容性

- 新增欄位不會破壞現有客戶端
- 欄位重命名將保持舊欄位 6個月
- 端點變更將維持重定向 6個月

## 11. 更新記錄

| 日期       | 版本 | 更新內容              | 更新人 |
|------------|------|-----------------------|--------|
| 2024-09-03 | 1.0  | 初始 API 規範建立     | Claude |