# AI Chatbot — Enhancement Roadmap v2

> **Phases 1–6B+** are complete. See `docs/ENHANCEMENT_ROADMAP_v1.md` for full details.

---

## Completed Phases Summary

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| **1** | Foundation | Data layer, multi-company/currency, security |
| **2** | Streaming | Frappe Realtime token streaming via Socket.IO |
| **3** | CRUD | Create/update/delete ERPNext records via chat |
| **4** | Finance Tools | 17 finance tools, ECharts integration |
| **5** | HRMS & CRM | 6 HRMS tools, 5 CRM tools with charts |
| **5A** | UX & Accessibility | File upload + Vision API, voice I/O, @mentions |
| **5B** | Enterprise Analytics | Permissions, dimensions, CFO dashboard, consolidation, plugins |
| **6** | Settings & Gemini | Unified provider config, Gemini, token/cost tracking |
| **6A** | UI Overhaul | Claude-style sidebar, dark mode, process indicators, search |
| **6B** | Multi-Dim Analytics | Hierarchical grouping engine, GL Entry finance, BI cards |
| **6B+** | Parent-Child Context | Session-aware multi-company, fuzzy company resolution, company dimension, prompt fixes |

---

## Current Architecture Reference

```
ai_chatbot/                     # Python package (backend)
├── api/
│   ├── chat.py                 # Chat API (multi-round tool calls, up to 5 rounds)
│   ├── streaming.py            # Streaming API (Frappe Realtime)
│   └── files.py                # File upload + Vision API
├── chatbot/doctype/            # Frappe DocTypes
│   ├── chatbot_settings/       # Provider config, feature toggles
│   ├── chatbot_conversation/   # Conversation with session_context JSON
│   └── chatbot_message/        # Messages with tool_calls JSON
├── core/
│   ├── config.py               # Company resolution (with fuzzy match), fiscal year, limits
│   ├── consolidation.py        # Parent/child company detection
│   ├── prompts.py              # System prompt builder (multi-company context, guidelines)
│   ├── session_context.py      # Per-conversation session vars (subsidiaries, currency)
│   ├── token_optimizer.py      # Context compression (last 20 msgs, strip charts)
│   └── token_tracker.py        # Token usage recording
├── data/
│   ├── grouping.py             # Multi-dimensional grouping engine (company, territory, etc.)
│   ├── analytics.py            # Generic aggregation helpers
│   ├── charts.py               # ECharts option builders
│   └── currency.py             # Currency response wrapper
├── tools/
│   ├── registry.py             # Tool registration + plugin loading
│   ├── session.py              # set_include_subsidiaries, set_target_currency
│   ├── selling.py              # Sales analytics tools
│   ├── buying.py               # Purchasing tools
│   ├── stock.py                # Inventory tools
│   ├── account.py              # Accounting tools
│   ├── crm.py                  # CRM tools
│   ├── hrms.py                 # HR tools
│   └── finance/                # Finance sub-package
│       ├── analytics.py        # Multi-dimensional summary tool
│       ├── gl_analytics.py     # GL Entry-based finance
│       ├── cfo.py              # CFO dashboard
│       ├── profitability.py    # Profitability analysis
│       ├── ratios.py           # Financial ratios
│       ├── budget.py           # Budget analysis
│       ├── cash_flow.py        # Cash flow analysis
│       ├── receivables.py      # Receivables aging
│       ├── payables.py         # Payables aging
│       └── working_capital.py  # Working capital analysis
└── utils/ai_providers.py       # OpenAI, Claude, Gemini API integration

frontend/                       # Vue 3 SPA
├── src/
│   ├── pages/ChatView.vue      # Main chat interface
│   ├── components/
│   │   ├── Sidebar.vue         # Conversation list, search, dark mode
│   │   ├── ChatMessage.vue     # Message rendering (markdown, charts, tables)
│   │   ├── ChatInput.vue       # Input with @mentions, file upload
│   │   └── charts/
│   │       ├── BiCards.vue      # BI metric cards
│   │       └── HierarchicalTable.vue  # Nested data tables
│   └── utils/
│       ├── api.js              # ChatAPI singleton with CSRF
│       └── markdown.js         # Markdown + code highlighting
└── vite.config.js              # Build config
```

### Key Patterns

- **Company resolution**: `get_company_filter(company)` → returns `str` or `list[str]`
- **Fuzzy company names**: `_resolve_company_name("Tara Technologies")` → `"Tara Technologies (Demo)"`
- **Multi-round tools**: Both streaming and non-streaming paths support up to 5 tool-call rounds
- **Session context**: `include_subsidiaries` and `target_currency` persist per conversation
- **All tools** use `get_company_filter()` (not `get_default_company()`) for queries
- **All monetary aggregations** use `base_*` fields and `build_currency_response()`
- **Grouping engine**: 7 built-in dimensions (company, territory, customer_group, customer, item_group, cost_center, department) + dynamic accounting dimensions

---

## Phase 6C: Workspace, Help & Language Selection

**Goal:** Frappe workspace for desk access, user help with sample prompts, response language in chat UI.

**Priority:** Low

### 6C.1 Workspace

**Files:** `chatbot/workspace/ai_chatbot/ai_chatbot.json` (new)

Create a workspace similar to CRM's pattern — a landing page with:
- Shortcut to the chatbot (`/ai-chatbot`)
- Shortcuts to Chatbot Settings, Conversations, Messages (for admin)
- Number cards: total conversations, messages today, token usage
- Custom block with quick-access link

### 6C.2 User Help Button

**Files:** `ChatInput.vue` (or new `HelpModal.vue`), `SAMPLE_USER_PROMPT.md` (new)

- Add a help icon button alongside the send button
- On click, show a modal with sample prompts and expected results
- Prompts organized by category (Sales, Finance, HR, etc.)
- Each prompt shows the expected output format (table, chart, number)

### 6C.3 Response Language Selection in Chat UI

**Files:** `Sidebar.vue` or `ChatView.vue`, `api/chat.py`

- Move "Response Language" from Chatbot Settings to the chat UI
- Add a language selector dropdown below "New Chat" in the sidebar
- Per-conversation language preference (stored in conversation metadata)
- Remove `response_language` from Chatbot Settings (or keep as default fallback)

### 6C.4 Deliverables

| Item | Files |
|------|-------|
| Workspace | `chatbot/workspace/ai_chatbot/ai_chatbot.json` |
| Help button | Updated `ChatInput.vue`, `HelpModal.vue`, `SAMPLE_USER_PROMPT.md` |
| Language selector | Updated `Sidebar.vue`, `api/chat.py` |

**New dependencies:** None.

---

## Phase 7: Agentic RAG — Vector Search + Multi-Agent Orchestration

**Goal:** Implement a full Agentic RAG system — combining vector-based document retrieval with multi-agent orchestration, planning, and iterative refinement.

### 7.1 RAG Foundation (`ai_chatbot/ai/rag/`)

```
ai_chatbot/ai/rag/
├── __init__.py
├── embeddings.py      # Embedding generation (OpenAI/local)
├── vector_store.py    # ChromaDB interface
├── chunker.py         # Document chunking strategies
└── retriever.py       # Query → retrieve → rank → return
```

**embeddings.py:**
- `generate_embedding(text)` — uses OpenAI `text-embedding-3-small` or local model
- Batch embedding support for document indexing

**vector_store.py:**
- ChromaDB as the default vector store (runs locally, no external service needed)
- `add_documents(chunks, embeddings, metadata)` — index documents
- `search(query_embedding, n_results=5, filters=None)` — similarity search
- `delete_documents(source_id)` — remove indexed documents
- Collection per company (multi-company isolation): `knowledge_{company_slug}`

**chunker.py:**
- `chunk_text(text, chunk_size=500, overlap=50)` — simple text chunking
- `chunk_document(file_path)` — PDF, DOCX, TXT extraction + chunking
- Metadata preservation (source document, page number, section)

**retriever.py:**
- `retrieve_context(query, company=None, n_results=5)` — embed query → search → return ranked chunks
- `evaluate_relevance(query, chunks)` — scores retrieved chunks for relevance (used by agents)
- `requery(original_query, feedback)` — refine search terms based on agent feedback

### 7.2 Agent Framework (`ai_chatbot/ai/agents/`)

```
ai_chatbot/ai/agents/
├── __init__.py
├── base_agent.py          # Abstract agent interface
├── orchestrator.py        # Routes queries to appropriate agent(s)
├── planner_agent.py       # Decomposes complex queries into steps
├── analyst_agent.py       # Data analysis with tool calling
└── document_agent.py      # Document retrieval and synthesis
```

**orchestrator.py:**
- Classifies incoming query: simple (generative) vs. data (tool-based) vs. knowledge (RAG) vs. complex (multi-step)
- Routes to appropriate agent or combination
- Manages agent execution loop with max iterations
- Combines tool results with RAG context when both are needed

**planner_agent.py:**
- Breaks complex queries into sub-tasks
- Example: "Compare Q3 vs Q4 sales and check if we're on track for budget" →
  1. Get Q3 sales (tool call)
  2. Get Q4 sales (tool call)
  3. Get budget for current year (tool call)
  4. Synthesize comparison (generation)

**analyst_agent.py:**
- Specialized for data queries
- Can chain multiple tool calls
- Evaluates whether results are sufficient or needs more data

**document_agent.py:**
- Retrieves from vector store via `retriever.py`
- Evaluates relevance of retrieved chunks
- Can re-query with refined search terms if initial results are poor
- Synthesizes answers from multiple document sources

### 7.3 Memory System (`ai_chatbot/ai/memory/`)

```
ai_chatbot/ai/memory/
├── __init__.py
├── conversation_memory.py    # Short-term: current conversation context
├── knowledge_memory.py       # Long-term: persistent knowledge from RAG
└── memory_manager.py         # Manages context window allocation
```

**memory_manager.py:**
- Allocates token budget across: system prompt, memory, RAG context, conversation history, tool results
- Prunes oldest messages when context limit approached
- Prioritizes recent and relevant context

### 7.4 Knowledge Base DocType & Indexing

**Chatbot Knowledge Base** (new DocType):
- Fields: `title`, `source_type` (File/ERPNext Record/URL), `source_reference`, `company`, `status` (Indexed/Pending/Failed), `chunk_count`, `last_indexed`
- Tracks what has been indexed into the vector store

**Indexing pipeline:**
- **Manual:** Upload PDF/DOCX via a "Knowledge Base" page in the frontend
- **Automatic:** Index key ERPNext records (Items, Customers, Suppliers, policies) via scheduled task
- **Incremental:** Only re-index documents that have changed since last indexing

### 7.5 Frontend

```
frontend/src/
├── pages/
│   └── KnowledgeBaseView.vue   # Document upload and management
├── components/
│   ├── chat/
│   │   └── AgentThinking.vue   # Shows agent reasoning steps
│   └── documents/
│       ├── DocumentUploader.vue # File upload with drag-and-drop
│       └── DocumentList.vue     # List of indexed documents
```

### 7.6 Deliverables

| Item | Files |
|------|-------|
| RAG engine | `ai/rag/embeddings.py`, `vector_store.py`, `chunker.py`, `retriever.py` |
| Agent framework | `ai/agents/base_agent.py`, `orchestrator.py`, `planner_agent.py`, `analyst_agent.py`, `document_agent.py` |
| Memory system | `ai/memory/conversation_memory.py`, `knowledge_memory.py`, `memory_manager.py` |
| Knowledge Base DocType | `chatbot/doctype/chatbot_knowledge_base/` |
| Indexing pipeline | Scheduled task in `hooks.py` |
| Frontend | `KnowledgeBaseView.vue`, `DocumentUploader.vue`, `DocumentList.vue`, `AgentThinking.vue` |
| Chat integration | Updated `api/chat.py` to use orchestrator |

**New dependencies:**
- **Backend:** `chromadb`, `openai` (for embeddings), `pypdf` (PDF extraction), `python-docx` (DOCX extraction)
- **Frontend:** None

---

## Phase 8: Intelligent Document Processing (IDP)

**Goal:** Extract data from uploaded documents (invoices, receipts, POs) and create ERPNext records. Includes data comparison and reconciliation.

### 8.1 File Upload Infrastructure (Completed in Phase 5A)

File upload and Vision API support was implemented in Phase 5A:
- `api/files.py` — upload endpoint, base64 encoding, vision content builder
- Frontend: file picker + drag-and-drop in ChatInput
- Frappe File DocType storage with `is_private=True`
- Image attachments sent to LLM Vision API (OpenAI & Claude)

### 8.2 Document Extraction (`ai_chatbot/idp/`)

```
ai_chatbot/idp/
├── __init__.py
├── extractors/
│   ├── base_extractor.py      # Abstract extractor interface
│   ├── invoice_extractor.py   # Invoice data extraction (via LLM vision)
│   ├── receipt_extractor.py   # Receipt processing
│   └── generic_extractor.py   # Generic document extraction
├── validators/
│   ├── schema_validator.py    # Validates extracted data against DocType schema
│   └── business_rules.py      # Business rule validation
└── mappers/
    ├── base_mapper.py         # Abstract mapper
    ├── invoice_mapper.py      # Maps extracted data → Purchase Invoice
    ├── supplier_mapper.py     # Maps extracted data → Supplier
    └── item_mapper.py         # Maps extracted data → Item
```

**Extraction approach:**
- Use GPT-4 Vision or Claude Vision to extract structured data from document images
- No OCR dependency for initial version (LLM vision is more accurate)
- Fallback to OCR (pytesseract) for high-volume, lower-cost processing

**Mapping flow:**
1. User uploads document (PDF/image) in chat
2. LLM Vision extracts structured data (supplier, items, amounts, dates)
3. Validator checks against ERPNext schema and business rules
4. Mapper creates draft ERPNext document
5. User reviews and confirms (reuses Phase 3 confirmation pattern)
6. Document is submitted

### 8.3 Data Comparison & Reconciliation

**Files:** `ai_chatbot/idp/comparison.py` (new), `ai_chatbot/tools/operations/reconcile.py` (new)

**Use case:** User attaches a client's Purchase Order PDF to a Sales Order — system compares and highlights discrepancies.

**Reconciliation tool:**
```python
@register_tool(
    name="compare_document_with_record",
    category="operations",
    description="Compare an uploaded document with an ERPNext record and highlight differences",
    parameters={
        "file_url": {"type": "string", "description": "URL of the uploaded file to compare"},
        "doctype": {"type": "string", "description": "ERPNext DocType to compare against"},
        "docname": {"type": "string", "description": "Document name to compare against"},
    },
)
```

### 8.4 Frontend

```
frontend/src/
├── pages/
│   └── DocumentProcessingView.vue
├── components/
│   └── idp/
│       ├── DocumentUploader.vue    # Upload with preview
│       ├── ExtractionResult.vue    # Show extracted fields, allow editing
│       └── MappingPreview.vue      # Preview ERPNext document before creation
```

### 8.5 Deliverables

| Item | Files |
|------|-------|
| Extractors | `idp/extractors/invoice_extractor.py`, `receipt_extractor.py`, `generic_extractor.py` |
| Validators | `idp/validators/schema_validator.py`, `business_rules.py` |
| Mappers | `idp/mappers/invoice_mapper.py`, `supplier_mapper.py`, `item_mapper.py` |
| Comparison | `idp/comparison.py`, `tools/operations/reconcile.py` |
| Frontend | `DocumentProcessingView.vue`, extraction/mapping components |
| DocType | `chatbot_document_queue` — tracks processing status |

**New dependencies:**
- **Backend:** `pypdf` (if not added in Phase 7), `Pillow`, optionally `pytesseract` + `pdf2image`, `openpyxl` (Excel parsing)
- **Frontend:** None

---

## Phase 9: Predictive Analytics & ML

**Goal:** Add forecasting and prediction capabilities using statistical and ML models.

### 9.1 Predictive Tools (`ai_chatbot/tools/predictive/`)

```
ai_chatbot/tools/predictive/
├── __init__.py
├── demand_forecast.py         # Item demand forecasting
├── sales_forecast.py          # Revenue forecasting
├── cash_flow_forecast.py      # Cash flow projections
└── anomaly_detection.py       # Detect unusual patterns
```

**Approach:** Start with statistical models (moving averages, exponential smoothing) before adding ML.

**demand_forecast.py:**
- `forecast_demand(item_code, months_ahead=3, company=None)` — projects future demand based on historical sales
- Uses: time series decomposition, moving average, or Prophet (if installed)
- Returns forecast with confidence intervals + ECharts option

**sales_forecast.py:**
- `forecast_revenue(company, months_ahead=3, granularity="monthly")` — revenue projection
- `forecast_by_territory(company, months_ahead=3)` — geographic forecast

**cash_flow_forecast.py:**
- `forecast_cash_flow(company, months_ahead=3)` — projected inflows/outflows based on receivables, payables, and historical patterns

**anomaly_detection.py:**
- `detect_anomalies(company, from_date, to_date)` — flags unusual transactions
- Uses: statistical thresholds (z-score, IQR) — no ML needed for initial version

### 9.2 Deliverables

| Item | Files |
|------|-------|
| Forecast tools | `tools/predictive/demand_forecast.py`, `sales_forecast.py`, `cash_flow_forecast.py` |
| Anomaly detection | `tools/predictive/anomaly_detection.py` |
| Chart support | ECharts options in all forecast responses |
| Settings | `enable_predictive_tools` flag |

**New dependencies (optional, phased):**
- **Minimal:** `pandas`, `numpy` (likely already available in Frappe environment)
- **Enhanced:** `prophet` (Facebook's time series forecasting — optional)
- **Advanced (future):** `scikit-learn`, `xgboost` — only when needed

---

## Phase 10: Automation & Notifications

**Goal:** Scheduled reports, alerts, automated workflows, and auto-email triggered by chat or conditions.

### 10.1 Auto Email & Scheduled Reports

**Files:** `ai_chatbot/automation/scheduled_reports.py`, new DocType: `Chatbot Scheduled Report`

**Chatbot Scheduled Report** DocType:
- `report_name`, `prompt`, `recipients` (Table), `schedule` (Daily/Weekly/Monthly/Cron)
- `company`, `ai_provider`, `format` (Email HTML/PDF/Both), `enabled`, `last_run`

**Execution flow:**
1. Scheduler triggers based on schedule
2. System builds conversation context (system prompt + company)
3. Sends prompt to AI with tools enabled
4. Captures response (text + charts + tool results)
5. Formats as HTML email (renders markdown, embeds chart images)
6. Sends via `frappe.sendmail()`

### 10.2 Alert System

**Files:** `ai_chatbot/automation/alerts.py`, new DocType: `Chatbot Alert`

**Chatbot Alert** DocType:
- `alert_name`, `condition_type` (Threshold/Schedule/Event)
- `threshold_tool`, `threshold_field`, `threshold_operator`, `threshold_value`
- `notification_channels` (Table), `recipients` (Table), `company`, `enabled`

**Example alerts:**
- "Notify me when receivables exceed 500,000"
- "Alert when stock of Camera falls below 10"

### 10.3 Notification Channels

```
ai_chatbot/automation/notifications/
├── __init__.py
├── channels/
│   ├── email.py               # Email via frappe.sendmail
│   ├── whatsapp.py            # WhatsApp via Twilio (already a dependency)
│   └── slack.py               # Slack webhook integration
└── dispatcher.py              # Routes alerts to appropriate channels
```

### 10.4 Deliverables

| Item | Files |
|------|-------|
| Scheduled reports | `automation/scheduled_reports.py`, `Chatbot Scheduled Report` DocType |
| Alert engine | `automation/alerts.py`, `Chatbot Alert` DocType |
| Notifications | `automation/notifications/channels/email.py`, `whatsapp.py`, `slack.py` |
| Dispatcher | `automation/notifications/dispatcher.py` |
| Hooks | Updated `hooks.py` with scheduler_events |
| Settings | Alert/report configuration in Chatbot Settings |

**New dependencies:** `slack_sdk` (optional, for Slack integration). Twilio already present.

---

## Phase Summary

| Phase | Focus | Priority | Status | Dependencies |
|-------|-------|----------|--------|--------------|
| **6C** | Workspace & Help | Low | Planned | None |
| **7** | Agentic RAG | Medium | Planned | chromadb, pypdf, python-docx |
| **8** | IDP | Medium | Planned | Pillow, pytesseract (opt), openpyxl |
| **9** | Predictive | Low | Planned | pandas, numpy, prophet (opt) |
| **10** | Automation | Low | Planned | slack_sdk (opt) |

---

## Reference: Key Patterns

### Multi-Company Query Pattern
```python
from ai_chatbot.core.session_context import get_company_filter

def get_some_data(company=None):
    company = get_company_filter(company)  # Returns str or list[str]

    if isinstance(company, list):
        query = query.where(dt.company.isin(company))
    else:
        query = query.where(dt.company == company)

    return build_currency_response(result, company[0] if isinstance(company, list) else company)
```

### Multi-Currency Fields
| DocType | Use This (Base) | Not This (Transaction) |
|---------|-----------------|----------------------|
| Sales Invoice | `base_grand_total` | `grand_total` |
| Purchase Invoice | `base_grand_total` | `grand_total` |
| Sales Order | `base_grand_total` | `grand_total` |
| Payment Entry | `base_paid_amount` | `paid_amount` |

### Company Isolation for RAG (Phase 7)
Vector store collections namespaced by company: `knowledge_{company_slug}`
