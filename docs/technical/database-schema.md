# Database Schema Design

## 1. 概述

本文件定義了 `Codex-Scribe` 專案中使用的數據庫結構設計，主要涵蓋向量數據庫 (ChromaDB) 和圖形資料庫 (Neo4j)。

**目標讀者**: 開發者、數據庫管理員。

## 2. 向量數據庫 (ChromaDB)

- **目的**: 存儲程式碼和文本的向量嵌入，用於高效的語義相似性搜索。
- **客戶端**: `chromadb` Python client
- **數據庫結構**:
    - **Collection**: 每個被索引的儲存庫都將在 ChromaDB 中擁有一個獨立的 Collection。
        - **命名慣例**: 將 GitHub URL 中的 `/` 和 `.` 替換為 `_`。
        - **範例**: `https://github.com/hao0608/Codex-Scribe` -> `github_com_hao0608_Codex-Scribe`
    - **Document**: 每個 Document 代表一個被分割的程式碼或文本塊 (chunk)。
    - **Embedding**: 每個 Document 都關聯一個由嵌入模型生成的向量。
    - **Metadata**: 每個 Document 都附帶一組豐富的元數據，用於過濾和提供上下文。

### 2.1 Metadata 結構

每個存儲在 ChromaDB 中的 Document 都將包含以下 Metadata 欄位：

```python
class ChromaDocumentMetadata(BaseModel):
    """
    Pydantic model for metadata stored in ChromaDB.
    """
    file_path: str          # 原始文件在儲存庫中的路徑
    language: str           # 程式語言 (e.g., "python", "markdown")
    start_line: int         # 該 chunk 在原始文件中的起始行號
    end_line: int           # 該 chunk 在原始文件中的結束行號
    chunk_hash: str         # 該 chunk 內容的 SHA256 hash，用於去重
    repository_url: str     # 所屬的 GitHub 儲存庫 URL
    indexed_at: datetime    # 索引時間戳
```

- **查詢過濾**: 可以使用 Metadata 進行查詢前的過濾。例如，只在 `.py` 文件中搜索。
- **上下文提供**: 在檢索到結果後，Metadata 可以幫助我們精確地定位到原始程式碼的位置。

## 3. 圖形資料庫 (Neo4j)

- **目的**: 存儲程式碼的結構化知識，捕捉實體（文件、類、函數）及其之間的關係。
- **查詢語言**: Cypher
- **數據模型**: 屬性圖模型 (Property Graph Model)

### 3.1 節點 (Nodes)

- **`Repository`**: 代表一個被索引的 GitHub 儲存庫。
    - **屬性**: `url` (string, 唯一), `name` (string)
- **`File`**: 代表一個源碼文件。
    - **屬性**: `path` (string, 唯一), `language` (string), `checksum` (string)
- **`Class`**: 代表一個類別定義。
    - **屬性**: `name` (string), `start_line` (int), `end_line` (int)
- **`Function`**: 代表一個函式或方法定義。
    - **屬性**: `name` (string), `signature` (string), `start_line` (int), `end_line` (int)

### 3.2 關係 (Relationships)

- **`:CONTAINS`**:
    - `(Repository)-[:CONTAINS]->(File)`
    - `(File)-[:CONTAINS]->(Class)`
    - `(File)-[:CONTAINS]->(Function)`
    - `(Class)-[:CONTAINS]->(Function)` (用於類別方法)
- **`:IMPORTS`**:
    - `(File)-[:IMPORTS]->(File)`
    - `(File)-[:IMPORTS]->(Class)`
    - `(File)-[:IMPORTS]->(Function)`
- **`:CALLS`**:
    - `(Function)-[:CALLS]->(Function)`
- **`:INHERITS_FROM`**:
    - `(Class)-[:INHERITS_FROM]->(Class)`

### 3.3 Cypher 查詢範例

- **查找特定函式的所有調用者**:
    ```cypher
    MATCH (caller:Function)-[:CALLS]->(callee:Function {name: 'process_payment'})
    RETURN caller.name, caller.signature
    ```
- **分析修改一個類別可能產生的影響**:
    ```cypher
    MATCH (c:Class {name: 'User'})<-[:IMPORTS]-(f:File)
    RETURN f.path
    ```
- **可視化文件之間的導入關係**:
    ```cypher
    MATCH p=(f1:File)-[:IMPORTS]->(f2:File)
    WHERE f1.path STARTS WITH 'src/core' AND f2.path STARTS WITH 'src/utils'
    RETURN p
    ```

## 4. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
