# Monitoring and Observability Guide

## 1. 概述

本文件定義了 `Codex-Scribe` 專案的監控、日誌記錄和可觀測性 (Observability) 策略。有效的監控對於確保系統在生產環境中的健康、性能和可靠性至關重要。

**目標讀者**: 開發者、維運 (DevOps) 工程師、SRE。

## 2. 監控的四大支柱

我們將圍繞以下四個核心領域建立可觀測性：

1.  **日誌 (Logging)**: 記錄離散的事件。
2.  **指標 (Metrics)**: 記錄可聚合的數值數據。
3.  **追蹤 (Tracing)**: 記錄跨越多個服務的單個請求的生命週期。
4.  **AI 可觀測性**: 專門針對 LLM 應用的監控。

## 3. 日誌 (Logging)

- **策略**: 採用結構化日誌記錄。
- **格式**: JSON。
- **函式庫**: Python 標準的 `logging` 模組，配置一個 `JSONFormatter`。
- **日誌級別**:
    - `DEBUG`: 詳細的開發資訊。
    - `INFO`: 系統正常運行的關鍵事件（如 API 請求、任務開始/結束）。
    - `WARNING`: 潛在問題或非嚴重錯誤。
    - `ERROR`: 導致操作失敗的錯誤。
    - `CRITICAL`: 導致系統崩潰的嚴重錯誤。
- **包含的上下文**:
    - `timestamp`
    - `level`
    - `message`
    - `request_id` (用於追蹤)
    - `service_name` (e.g., "api-service", "indexing-service")
    - 額外的結構化數據 (e.g., `user_id`, `task_id`)
- **雲端方案 (AWS)**:
    - 應用程式將日誌輸出到 `stdout`/`stderr`。
    - ECS/Lambda 將自動將這些日誌轉發到 **Amazon CloudWatch Logs**。
    - 使用 CloudWatch Logs Insights 進行查詢和分析。

## 4. 指標 (Metrics)

- **目標**: 監控系統的整體健康狀況和性能。
- **收集**:
    - **基礎設施指標**: CPU 使用率、內存使用率、網絡流量 (由 CloudWatch 自動收集)。
    - **應用指標**:
        - API 請求延遲 (latency)。
        - API 請求率 (request rate)。
        - API 錯誤率 (error rate, 4xx/5xx)。
        - 索引任務執行時間。
- **雲端方案 (AWS)**:
    - **Amazon CloudWatch Metrics**: 存儲和監控指標。
    - **Amazon CloudWatch Alarms**: 當指標超過閾值時（例如，API 錯誤率 > 5%），發送通知（如到 Slack 或 PagerDuty）。
    - **Amazon CloudWatch Dashboards**: 創建儀表板來可視化關鍵指標。

## 5. 追蹤 (Tracing)

- **目標**: 理解單個請求在分佈式系統中的完整路徑和延遲瓶頸。
- **標準**: OpenTelemetry。
- **函式庫**: `opentelemetry-python`。
- **實現**:
    - 在 API Gateway 或應用程式入口處生成一個唯一的 `trace_id`。
    - 通過中間件將 `trace_id` 注入到所有後續的函式呼叫和服務間通信中。
    - 每個主要操作（如數據庫查詢、LLM 呼叫）都應創建一個 `span`。
- **雲端方案 (AWS)**:
    - **AWS X-Ray**: 收集、可視化和分析追蹤數據。

## 6. AI 可觀測性

- **目標**: 專門監控 LLM 應用的性能和品質。
- **工具**: **LangSmith** (來自 LangChain) 或類似的第三方服務 (WhyLabs, Arize AI)。
- **監控的關鍵 AI 指標**:
    - **LLM API 呼叫延遲和成本**: 追蹤每次呼叫 OpenAI 等服務的耗時和費用。
    - **Token 使用量**: 監控每個請求的提示 (prompt) 和完成 (completion) token 數量。
    - **提示/輸出追蹤**: 記錄每個 LLM 互動的完整提示和輸出，以便於除錯。
    - **回答品質評估**:
        - **用戶回饋**: 在 UI 中提供 "讚/踩" 按鈕，收集用戶對回答品質的直接回饋。
        - **自動評估**: 定期運行基於 `Ragas` 的評估流程，監控 Faithfulness, Relevancy 等指標的變化趨勢。
- **整合**:
    - 將 LangSmith 與我們的 LangChain 應用整合，只需設置幾個環境變數。
    - LangSmith 將自動捕獲所有鏈 (chain) 和代理程式 (agent) 的執行軌跡。

## 7. 儀表板與告警

- **儀表板 (Dashboard)**:
    - **業務指標**: 每日分析任務數量、成功率。
    - **API 性能**: P95/P99 延遲、錯誤率、請求數。
    - **AI 指標**: 平均 LLM 呼叫延遲、token 成本、用戶回饋分數。
- **告警 (Alerting)**:
    - **高優先級 (PagerDuty)**: 5xx 錯誤率激增、API 服務不可用。
    - **中優先級 (Slack)**: P99 延遲超過閾值、索引任務失敗。
    - **低優先級 (Email/Slack)**: LLM API 成本超出預算。

## 8. 更新記錄

| 日期       | 版本 | 更新內容           | 更新人 |
|------------|------|--------------------|--------|
| 2025-07-24 | 1.0  | 初始版本建立       | Cline  |
