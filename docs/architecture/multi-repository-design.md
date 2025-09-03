# Multi-Repository Architecture Design

## 1. 概述

本文件定義了 `Codex-Scribe` 系統的多儲存庫支援架構。此設計解決了原有系統的單一儲存庫限制，使系統能夠同時管理和查詢多個程式碼儲存庫，並確保資料隔離和查詢效率。

**目標讀者**: 開發者、架構師

## 2. 現有問題分析

### 2.1 當前限制
- **單一資料庫實例**: 使用一個 ChromaDB collection 和一個 Neo4j 資料庫實例
- **資料覆蓋風險**: `IndexRepositoryUseCase.clear_database()` 會清除整個資料庫
- **無儲存庫隔離**: 無法區分不同儲存庫的資料
- **查詢混淆**: 無法針對特定儲存庫進行查詢

### 2.2 業務需求
- 支援多個程式碼儲存庫同時存在
- 儲存庫間資料完全隔離
- 可針對特定儲存庫或跨儲存庫查詢
- 儲存庫管理功能（新增、刪除、列表）

## 3. 架構設計方案

### 3.1 選擇的方案：Collection/Database per Repository

**ChromaDB 設計**:
```python
# 每個儲存庫使用獨立的 collection
collection_name = f"repo_{repository_name.replace('/', '_').replace('-', '_')}"
```

**Neo4j 設計**:
```python
# 每個儲存庫的節點添加專用標籤
node.labels.append(f"Repo_{repository_name.replace('/', '_')}")
```

### 3.2 儲存庫命名規範

**命名轉換規則**:
- GitHub URL: `https://github.com/user/repo-name`
- 儲存庫識別符: `user/repo-name`
- ChromaDB Collection: `repo_user_repo_name`
- Neo4j Label: `Repo_user_repo_name`

**特殊字元處理**:
- `/` → `_`
- `-` → `_`
- `.` → `_`

## 4. 資料模型設計

### 4.1 ChromaDB 模型

```python
class MultiRepoChromaDBClient:
    def __init__(self, path: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self._collections: Dict[str, Collection] = {}
    
    def get_collection(self, repository_name: str) -> Collection:
        collection_name = self._normalize_repo_name(repository_name)
        if collection_name not in self._collections:
            self._collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name
            )
        return self._collections[collection_name]
```

### 4.2 Neo4j 模型

```python
class MultiRepoNeo4jService:
    def add_node(self, node: BaseNode, repository_name: str) -> None:
        repo_label = f"Repo_{self._normalize_repo_name(repository_name)}"
        node.labels.append(repo_label)
        # 添加儲存庫屬性
        node.properties["repository"] = repository_name
```

### 4.3 儲存庫元資料

```python
@dataclass
class RepositoryMetadata:
    name: str  # user/repo-name
    display_name: str
    url: str
    indexed_at: datetime
    file_count: int
    chunk_count: int
    node_count: int
    edge_count: int
    status: RepositoryStatus
```

## 5. API 設計

### 5.1 儲存庫管理 API

```python
# 列出所有儲存庫
GET /api/v1/repositories

# 取得特定儲存庫資訊
GET /api/v1/repositories/{repo_name}

# 索引新儲存庫
POST /api/v1/repositories
{
  "url": "https://github.com/user/repo-name",
  "include_dirs": ["src/", "docs/"]
}

# 刪除儲存庫
DELETE /api/v1/repositories/{repo_name}

# 重新索引儲存庫
POST /api/v1/repositories/{repo_name}/reindex
```

### 5.2 查詢 API 增強

```python
# 在特定儲存庫中查詢
POST /api/v1/repositories/{repo_name}/query
{
  "query": "How does authentication work?",
  "search_type": "hybrid"
}

# 跨儲存庫查詢
POST /api/v1/query
{
  "query": "How does authentication work?",
  "repositories": ["user/repo1", "user/repo2"],  # 可選，預設所有
  "search_type": "hybrid"
}
```

## 6. 儲存結構

### 6.1 目錄結構
```
data/
├── chroma_db/           # ChromaDB 資料
│   ├── repo_user_repo1/ # 儲存庫 1 的向量資料
│   └── repo_user_repo2/ # 儲存庫 2 的向量資料
├── neo4j/              # Neo4j 資料（透過 Docker）
└── metadata/           # 儲存庫元資料
    ├── repositories.json
    └── indexing_logs/
```

### 6.2 元資料儲存
```json
{
  "repositories": {
    "user/repo1": {
      "display_name": "User Repository 1",
      "url": "https://github.com/user/repo1",
      "indexed_at": "2024-01-01T12:00:00Z",
      "file_count": 150,
      "chunk_count": 1200,
      "node_count": 300,
      "edge_count": 450,
      "status": "indexed"
    }
  }
}
```

## 7. 遷移策略

### 7.1 向後相容性
- 現有單一儲存庫資料自動遷移到 `default` 命名空間
- 提供遷移腳本 `scripts/migrate_to_multi_repo.py`

### 7.2 遷移步驟
1. 備份現有資料
2. 建立新的多儲存庫結構
3. 遷移現有資料到 `default` 儲存庫
4. 更新 API 端點
5. 測試驗證

## 8. 效能考量

### 8.1 查詢效能
- **單一儲存庫查詢**: 直接查詢對應 collection/標籤
- **跨儲存庫查詢**: 並行查詢多個 collection，結果合併排序
- **快取策略**: 常用儲存庫的 collection 物件快取

### 8.2 儲存效能
- **獨立索引**: 各儲存庫獨立索引，互不影響
- **增量更新**: 支援單一儲存庫的增量索引
- **並行處理**: 多儲存庫可並行索引

## 9. 安全性考量

### 9.1 存取控制
- 儲存庫級別的存取權限控制
- API 金鑰與儲存庫權限綁定
- 敏感儲存庫的獨立加密

### 9.2 資料隔離
- 完全的物理資料隔離
- 查詢時的權限驗證
- 日誌記錄和稽核追蹤

## 10. 監控和維護

### 10.1 監控指標
- 各儲存庫的索引狀態
- 查詢效能統計
- 儲存空間使用情況
- 錯誤率和回應時間

### 10.2 維護操作
- 定期的索引健康檢查
- 過期資料清理
- 效能優化建議

## 11. 更新記錄

| 日期       | 版本 | 更新內容                    | 更新人 |
|------------|------|----------------------------|--------|
| 2024-09-03 | 1.0  | 初始多儲存庫架構設計文件建立 | Claude |