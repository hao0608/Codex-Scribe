# Usage Examples

## 1. 概述

本文件提供了一系列 `Codex-Scribe` 的使用範例，展示了如何利用其混合式檢索功能來回答各種類型的程式碼問題。

## 2. 查詢範例

### 2.1 語義查詢 (Vector Search)

這種類型的查詢通常是關於「是什麼」或「如何工作」。

**範例 1: 查詢一個類別的功能**
```
How does the CodeParser work?
```

**預期回答**:
> CodeParser 是一個用於解析程式碼並提取其中結構信息以構建知識圖譜的工具。它使用 Tree-sitter 來解析 Python 程式碼...

**範例 2: 查詢一個服務的目的**
```
What is the purpose of the embedding service?
```

### 2.2 結構查詢 (Graph Query)

這種類型的查詢通常是關於「誰呼叫誰」或「什麼在哪裡」。

**範例 1: 查詢一個函數的呼叫者**
```
Who calls the "parse" function?
```

**預期回答**:
> I couldn't find any callers for the function 'parse' in the indexed codebase.

**範例 2: 查詢一個類別包含的方法**
```
What methods are in the "CodeParser" class?
```

**預期回答**:
> `CodeParser` 類別包含以下方法：
> 1. `__init__`
> 2. `_extract_calls`
> 3. `_find_containing_scope`
> 4. `_execute_query`
> 5. `_extract_functions`
> 6. `_extract_imports`
> 7. `_extract_classes`
> 8. `parse`

### 2.3 混合查詢

這種類型的查詢可能需要結合向量搜索和圖形查詢的結果。

**範例 1: 查詢一個服務的使用者**
```
What components use the Neo4j service?
```

**預期回答**:
> 根據提供的上下文，Neo4jService 主要被以下組件所使用：
> 1. `IndexRepositoryUseCase`
> 2. `main` 函數

## 3. API 使用範例

### 3.1 索引一個新的儲存庫
```bash
curl -X POST http://localhost:8000/index \
     -H "Content-Type: application/json" \
     -d '{
           "repo_url": "https://github.com/user/repo"
         }'
```

### 3.2 提出一個問題
```bash
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{
           "query": "How does authentication work?"
         }'
```

## 4. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-30 | 1.0  | 初始版本建立       | Cline  |
