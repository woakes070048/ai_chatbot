# AI Chatbot — Test Plans v2

> **Test plans for Phases 1–6B+** are in `docs/TEST_v1.md`.

---

## Prerequisites

- Frappe bench running (`bench start`)
- At least one company with transactions in the current fiscal year
- Chatbot Settings configured with a valid AI provider (OpenAI or Claude)
- Finance tools enabled in Chatbot Settings

---

## Regression Tests (Run Before Each Phase)

These quick checks confirm prior functionality still works after any new phase.

### R.1 Basic Chat
- Send a greeting → AI responds conversationally
- Ask a general knowledge question → AI responds without tool calls

### R.2 Sales Query
- Ask: `What are the total sales this month?`
- Expected: Revenue figure with currency symbol, date range, company name

### R.3 Finance Dashboard
- Ask: `Show financial overview`
- Expected: BI cards with key metrics (revenue, expenses, profit, etc.)

### R.4 Multi-Company (if parent company exists)
- Ask: `Show consolidated revenue`
- Expected: AI auto-includes subsidiaries, shows aggregated data
- Ask: `Show sales of [specific company name]`
- Expected: Data for that specific company only (fuzzy name resolution)

### R.5 Grouping
- Ask: `Show sales by territory`
- Expected: Hierarchical table with territory breakdown
- Ask: `Show sales by company, territory`
- Expected: Two-level hierarchy — company → territory

### R.6 Dark Mode
- Toggle dark mode in sidebar → UI renders correctly

### R.7 Streaming
- Ask any data question → response streams token-by-token with process indicator

---

## Phase 6C: Workspace, Help & Language

### 6C.1 Workspace
- Navigate to desk → find AI Chatbot workspace
- Verify shortcuts: chatbot link, settings, conversations, messages
- Verify number cards display correctly

### 6C.2 Help Button
- Click help icon next to send button
- Modal opens with categorized sample prompts
- Click a sample prompt → it populates the input

### 6C.3 Language Selector
- Change language in sidebar dropdown
- Ask a question → AI responds in selected language
- New conversation → language preference persists per conversation

---

## Phase 7: Agentic RAG

### 7.1 RAG Indexing
- Upload a PDF to Knowledge Base → document is chunked and indexed
- Check ChromaDB collection exists for the company
- Re-upload same document → incremental re-indexing (no duplicates)

### 7.2 RAG Retrieval
- Ask a question about an indexed document → AI retrieves relevant chunks
- Ask about a non-indexed topic → AI responds without RAG (falls back to tools or general knowledge)

### 7.3 Agent Orchestration
- Ask a simple data question → routes to analyst agent (tool call)
- Ask about a document → routes to document agent (RAG)
- Ask a complex multi-step question → routes to planner agent
- Verify agent reasoning steps display in UI (AgentThinking component)

### 7.4 Memory System
- Long conversation (20+ messages) → context compression activates
- Relevant earlier context is preserved, old messages pruned

---

## Phase 8: IDP

### 8.1 Document Extraction
- Upload an invoice PDF → structured data extracted (supplier, items, amounts)
- Verify extracted fields match the document content

### 8.2 Record Creation
- Extracted data → preview ERPNext document → user confirms → document created
- Verify created document matches extracted data

### 8.3 Reconciliation
- Upload a PO PDF and compare with a Sales Order → discrepancy report generated
- Verify field-by-field comparison is accurate

---

## Phase 9: Predictive Analytics

### 9.1 Demand Forecast
- Ask: `Forecast demand for [item] for next 3 months`
- Expected: Forecast with confidence intervals + ECharts chart

### 9.2 Revenue Forecast
- Ask: `Forecast revenue for next quarter`
- Expected: Revenue projection with trend chart

### 9.3 Anomaly Detection
- Ask: `Detect any anomalies in transactions this year`
- Expected: List of flagged transactions with explanations

---

## Phase 10: Automation

### 10.1 Scheduled Reports
- Create a scheduled report (weekly sales summary)
- Wait for schedule to trigger → email received with formatted report

### 10.2 Alerts
- Create a threshold alert (e.g., receivables > 500,000)
- Trigger the condition → notification received via configured channel

### 10.3 Notification Channels
- Test email notification → received
- Test WhatsApp notification (if Twilio configured) → received
- Test Slack notification (if configured) → received
