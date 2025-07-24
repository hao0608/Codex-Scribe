# Git Workflow Guide

## 1. 概述

本文件定義了 `Codex-Scribe` 專案的 Git 工作流程、分支管理策略和 Commit 規範。遵循此工作流程有助於保持程式碼庫的整潔、追蹤變更歷史並促進高效協作。

**目標讀者**: 所有參與此專案的開發者和 AI 代理程式。

## 2. 核心原則

- **主分支保護**: `main` 和 `develop` 分支受到保護，不允許直接推送 (push)。所有變更都必須通過拉取請求 (Pull Request) 合併。
- **功能分支開發**: 所有新功能和錯誤修復都在獨立的功能分支上進行。
- **清晰的 Commit 歷史**: 每個 commit 都應該是原子性的，並附有清晰、格式化的訊息。

## 3. 分支策略

本專案採用 **GitFlow** 的簡化版本。

### 3.1 主要分支

- **`main`**:
    - 代表生產就緒 (production-ready) 的穩定版本。
    - 只有在 `develop` 分支經過充分測試後才能合併到 `main`。
    - 合併到 `main` 時應創建一個 Git Tag 來標記版本號 (e.g., `v0.1.0`)。

- **`develop`**:
    - 開發過程中的主要整合分支。
    - 所有功能分支都從 `develop` 創建，並最終合併回 `develop`。
    - `develop` 分支應始終保持可構建和可測試的狀態。

### 3.2 功能分支 (`feature/*`)

- **命名規範**: `feature/<short-description>`
    - 範例: `feature/code-indexer`, `feature/streamlit-ui`
- **創建**: 從 `develop` 分支創建。
    - `git checkout develop`
    - `git pull`
    - `git checkout -b feature/new-feature-name`
- **生命週期**:
    - 開發完成後，向 `develop` 分支發起一個 Pull Request。
    - Code Review 通過並合併後，該功能分支應被刪除。

### 3.3 修復分支 (`fix/*` 或 `hotfix/*`)

- **`fix/*`**: 用於修復在 `develop` 分支上發現的非緊急 bug。流程與功能分支相同。
- **`hotfix/*`**: 用於修復在 `main` 分支上發現的緊急 bug。
    - **創建**: 從 `main` 分支創建。
    - **合併**: 完成後，必須同時合併回 `main` 和 `develop` 分支。

## 4. Commit 訊息規範

本專案遵循 **Conventional Commits** 規範。

### 4.1 格式

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### 4.2 類型 (`<type>`)

- `feat`: 新功能 (feature)。
- `fix`: 修復 bug。
- `docs`: 只修改了文檔。
- `style`: 不影響程式碼功能的格式變更（如空格、分號等）。
- `refactor`: 重構程式碼，既不是新增功能也不是修復 bug。
- `test`: 新增或修改測試。
- `chore`: 建置流程、輔助工具或依賴庫的變更。

### 4.3 範例

**簡單 Commit:**
```
feat: Add support for TypeScript file indexing
```

**帶有 Body 的 Commit:**
```
fix: Correctly handle empty files during indexing

The file processor would previously crash if it encountered an empty
source file. This commit adds a check to handle this case gracefully
by logging a warning and skipping the file.
```

**重大變更 (Breaking Change):**
```
refactor!: Change database schema for code chunks

The `CodeChunk` model schema has been updated to include a `language`
field. This is a breaking change and requires a database migration.

BREAKING CHANGE: The `embedding` field was renamed to `vector`.
```

## 5. Pull Request (PR) 流程

1.  **創建 PR**: 當功能分支開發完成後，向 `develop` 分支發起一個 PR。
2.  **描述**: PR 的描述應清晰說明此變更的目的和內容。如果相關，請連結到對應的 issue。
3.  **審查 (Review)**:
    - 至少需要一名審查者批准 (approve)。
    - CI/CD 檢查（如測試、linting）必須全部通過。
4.  **合併**:
    - 使用 **Squash and Merge** 將功能分支的多次 commit 合併為一個清晰的 commit 到 `develop` 分支。
    - 合併後，刪除源功能分支。

## 6. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
