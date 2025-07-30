# Phase 3: Knowledge Graph - Deep Code Understanding

## 1. 概述

本文件詳細描述了 `Codex-Scribe` 專案第三階段的開發計劃。此階段的目標是引入知識圖譜 (Knowledge Graph)，讓系統從僅僅理解程式碼的「語義」層面，進化到能夠理解程式碼的「結構和關係」，實現真正的深度專案理解。

**目標**: 賦予 AI 代理程式進行複雜依賴關係分析和影響評估的能力。

## 2. 功能與範圍

### 2.1 核心功能

- **AST 解析**: 使用 `tree-sitter` 解析程式碼，提取關鍵的程式碼結構元素，如類別、函式、導入語句和函式呼叫。
- **知識圖譜構建**: 將解析出的實體（Files, Classes, Functions）和它們之間的關係（`IMPORTS`, `DEFINES`, `CALLS`）存儲到圖形資料庫 (Neo4j) 中。
- **圖形資料庫整合**: 建立一個新的工具，允許 AI 代理程式查詢知識圖譜。
- **混合式檢索 (Hybrid Retrieval)**: 升級 AI 代理程式，使其能夠根據問題的性質，智能地選擇使用向量搜索（用於語義問題）或圖形查詢（用於結構問題），或兩者結合。

### 2.2 範圍限制 (Out of Scope)

- **實時圖譜更新**: 本階段的知識圖譜將通過離線索引管道定期更新，而非實時同步。
- **複雜的自然語言到 Cypher**: 初步將實現針對特定、預定義問題模式的圖形查詢，而非通用的自然語言到 Cypher 的轉換。

## 3. 技術棧

- **程式碼解析器**: tree-sitter, tree-sitter-python
- **圖形資料庫**: Neo4j
- **Python-Neo4j 驅動**: `neo4j`
- **其他**: 延續前序階段的技術棧。

## 4. 開發里程碑與任務分解

### 里程碑 1: AST 解析器與實體提取 (`feature/ast-parser`)

- [x] **安裝 `tree-sitter`**: 將 `tree-sitter` 和對應的語言文法（如 `tree-sitter-python`）整合到專案中。
- [x] **解析器模組 (`src/infrastructure/parser`)**:
    - 建立一個 `CodeParser` 類別。
    - 實作方法來遍歷 AST 並提取節點資訊。
- [x] **實體提取邏輯**:
    - 提取文件中的 `import` 語句。
    - 提取 `class` 和 `function` 的定義。
    - 提取函數內部的 `function call`。
- [x] **輸出**: 解析器的輸出應該是結構化的 Pydantic 物件列表，代表從單一文件中提取的所有實體和關係。

- [x] **修正與增強 `CodeParser`**:
    - [x] **修正呼叫來源識別**: 實作範圍追蹤，正確識別函式呼叫的來源 (函式或類別)。
    - [x] **修正單元測試**: 更新測試斷言，使其符合程式碼的實際行為。
    - [x] **改進類別-方法關係**: 為類別內的方法建立從 `ClassNode` 到 `FunctionNode` 的 `CONTAINS` 關係。
    - [x] **支援裝飾器**: 更新查詢以支援被裝飾的類別和函式。
    - [x] **效能優化**: 使用 `set` 提高重複節點的檢查效率。

### 里程碑 2: Neo4j 知識圖譜構建 (`feature/knowledge-graph`)

- [x] **設置 Neo4j**: 提供 Docker Compose 配置，以便在本地快速啟動一個 Neo4j 實例。
- [x] **圖形資料庫服務 (`src/infrastructure/database/graph_db.py`)**:
    - 建立一個 `Neo4jService` 來封裝與資料庫的連接和查詢操作。
    - 實作 `add_node` 和 `add_edge` 等基本方法。
- [x] **更新索引管道 (`scripts/index_repository.py`)**:
    - 在現有的索引流程中加入一個新步驟。
    - 在生成向量嵌入之後，調用 `CodeParser`。
    - 將解析出的實體和關係通過 `Neo4jService` 寫入圖形資料庫。
    - **節點**: `File`, `Class`, `Function`
    - **關係**: `CONTAINS`, `IMPORTS`, `CALLS`

### 里程碑 3: 混合式檢索與查詢 (`feature/hybrid-search`)

- [x] **圖形查詢工具**:
    - 在 `src/application/use_cases` 中建立一個新的工具 `GraphQueryTool`。
    - 該工具接收結構化查詢（或簡化的自然語言），將其轉換為 Cypher 查詢語句。
    - 範例查詢: "Find all functions that call the `process_payment` function."
- [x] **升級代理程式協調器**:
    - 將 `GraphQueryTool` 添加到代理程式可用的工具列表中。
- [x] **優化任務規劃器**:
    - 調整任務規劃器的提示，使其能夠識別需要進行圖形查詢的問題類型。
    - 代理程式現在可以決定是使用 `VectorSearchTool` 還是 `GraphQueryTool`。
    - **範例決策**:
        - "How does authentication work?" -> 使用向量搜索。
        - "What will be affected if I change the `User` model?" -> 使用圖形查詢。

## 5. 驗收標準

- **功能性**:
    - [x] 索引管道能夠成功解析專案程式碼並在 Neo4j 中建立對應的節點和關係。
    - [x] 能夠通過 Cypher 查詢，找出特定函數的所有調用者。
    - [x] AI 代理程式在被問及 "Which modules import the `GitHubService` class?" 時，能夠正確調用 `GraphQueryTool` 並返回準確結果。
- **性能**:
    - [x] 包含 AST 解析和圖譜構建的完整索引流程，其執行時間應在可接受範圍內（中型專案 < 15 分鐘）。
- **數據一致性**:
    - [x] Neo4j 中的節點數量應與專案中的文件、類和函數的實際數量大致相符。

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-30 | 1.1  | 完成所有里程碑和驗收標準 | Cline  |
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
