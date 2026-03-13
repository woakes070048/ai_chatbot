# AI Chatbot — Phase-wise Enhancement Roadmap

## Current State Summary (Post Phase 6B)

The AI Chatbot is a functional Frappe app with:

- **4 DocTypes:** Chatbot Settings (Single), Chatbot Conversation, Chatbot Message, Chatbot Token Usage
- **51+ tools** across 10 categories: CRM (5), Selling (8), Buying (6), Stock (6), Account (2), Finance (24 incl. CFO, GL analytics, multi-dimensional), HRMS (6), Operations (3), Consolidation (1)
- **3 AI providers:** OpenAI (GPT-4o), Claude (Sonnet 4.5), and Gemini (2.5 Flash) — unified single-provider configuration
- **Streaming:** Real-time token streaming via Frappe Realtime (Socket.IO/WebSocket) with process step indicators
- **CRUD:** Create, update, search ERPNext records via chat with confirmation pattern
- **ECharts:** Inline chart rendering (bar, line, pie, horizontal bar, multi-series) with multi-color palette
- **Multi-company & multi-currency:** All tools use `company` parameter and `base_*` fields
- **Consolidation:** Parent company detection, cross-subsidiary aggregation with currency conversion
- **Permissions:** DocType-based tool filtering — users only see tools they have access to
- **Accounting Dimensions:** Finance tools support cost_center, department, project filtering
- **Configurable prompts:** Custom persona, response language, custom instructions via settings
- **Financial analyst behaviour:** CFO-grade analysis behaviour when finance tools are enabled
- **Plugin system:** External apps register tools via `ai_chatbot_tool_modules` Frappe hook
- **Data layer:** `frappe.qb` Query Builder throughout — no raw SQL
- **Token optimization:** Conversation history trimming (configurable `max_context_messages`), tool result compression (strip echart_option, truncate large datasets)
- **Cost monitoring:** Per-request token usage tracking with estimated cost (Chatbot Token Usage DocType)
- **Vue 3 frontend:** Claude.AI-inspired sidebar (collapsible, date-grouped, search), wider AI messages, icon-only buttons
- **Dark mode:** OS-level `prefers-color-scheme` detection, Tailwind `dark:` classes across all components
- **Chat search:** Backend `search_conversations` endpoint + sidebar search UI with debounced input
- **Process indicators:** Real-time pipeline steps ("Preparing context...", "Executing Tool...", "Saving response...")
- **Personalized greeting:** Centered logo + "Hello, {name}!" on new conversations; input moves to bottom after first message
- **File upload:** Image/PDF/document upload with Vision API support (OpenAI, Claude & Gemini)
- **Voice I/O:** Speech-to-text input (Web Speech API) and text-to-speech output (SpeechSynthesis)
- **@Mention autocomplete:** `@company`, `@period`, `@cost_center`, `@department`, `@warehouse`, `@customer`, `@item`, `@accounting_dimension`
- **Favicon & Logo:** Custom orbital SVG (violet gradient, RGB dots) as favicon and AI assistant avatar
- **User Avatar:** User's profile image on right side of message bubbles; initials fallback. Personalized greeting shows large user avatar (not app logo)
- **Settings tabs:** Chatbot Settings organized into tabs (API Configuration, Tools, Query Configuration, Prompts, Streaming)
- **Multi-dimensional analytics:** Hierarchical grouping by territory, customer_group, customer, item_group, cost_center, department with period columns (monthly/quarterly/yearly)
- **GL Entry finance:** Trial balance, GL summary, account statement — authoritative accounting data from GL entries
- **BI metric cards:** CFO dashboard returns styled metric cards with YoY change percentages (Revenue, Net Profit, Cash, AR, AP)
- **Hierarchical tables:** Frontend renders indented data tables with group headers, subtotals, and bold formatting

---

## Design Principles (All Phases)

1. **Multi-Company by default:** Every tool that queries financial/transactional data MUST accept a `company` parameter. Default to the user's default company (`frappe.defaults.get_user_default("Company")`).
2. **Multi-Currency aware:** Monetary aggregations must use `base_grand_total` (company currency) or explicitly convert using ERPNext's currency exchange rates. Tool responses should include the currency code.
3. **Backward compatible:** Each phase must leave the app fully functional. No half-finished features merged.
4. **Incremental dependencies:** Only add Python/npm packages when the phase that needs them is being implemented.
5. **Frappe-native patterns:** Use Frappe ORM (`frappe.get_all`, `frappe.get_list`) instead of raw SQL. Use `frappe.qb` (Query Builder) for complex queries.
6. **Permission-aware:** Respect Frappe's permission model. Users should only access data they are authorized to see.

---

## Completed Phases

### Phase 1: Foundation ✅

Core framework (`core/config.py`, `constants.py`, `exceptions.py`, `logger.py`), data layer (`data/queries.py`, `analytics.py`, `currency.py`), tool registry (`tools/registry.py`), multi-company/currency refactor of all tools, SQL injection fixes.

### Phase 2: Streaming ✅

Token-by-token streaming via `frappe.publish_realtime` (Socket.IO/WebSocket through Redis Pub/Sub). Provider streaming for OpenAI and Claude. Frontend composable (`useStreaming.js`), streaming message rendering, auto-scroll, tool call display during stream.

### Phase 3: Data Operations (CRUD) ✅

Create/update/search tools (`tools/operations/`). Document creation (Lead, Opportunity, ToDo, Sales Order), status updates, fuzzy search. Two-step confirmation pattern for write operations. `enable_write_operations` settings flag.

### Phase 4: Finance Tools & Business Intelligence ✅

17 finance tools across 7 modules (receivables, payables, cash flow, budget, profitability, working capital, ratios). Enhanced selling (3), buying (2), stock (2) tools with charts. ECharts frontend integration (`EChartRenderer.vue`, `ChartMessage.vue`). Tool results persistence. Multi-color chart palette.

---

## Phase 5: HRMS Tools & Enhanced CRM ✅

**Goal:** Complete the HRMS placeholder and expand CRM capabilities.

### 5.1 HRMS Tools (`ai_chatbot/tools/hrms.py`) ✅

6 HRMS tools implemented, all with HRMS module detection and ECharts:

- `get_employee_count(company, department=None, status="Active")` — headcount with department breakdown
- `get_attendance_summary(company, from_date, to_date, department=None)` — attendance stats (present, absent, leave, half-day)
- `get_leave_balance(employee=None, leave_type=None, company=None)` — leave balances by type
- `get_payroll_summary(company, from_date, to_date)` — total salary, deductions, net pay with chart
- `get_department_wise_salary(company, month=None)` — salary by department with pie chart
- `get_employee_turnover(company, from_date, to_date)` — joining vs leaving rate with trend chart

### 5.2 Enhanced CRM Tools (`ai_chatbot/tools/crm.py`) ✅

5 CRM tools (3 new + 2 updated with ECharts):

- `get_lead_conversion_rate(company, from_date, to_date)` — lead-to-opportunity conversion rate with funnel chart
- `get_lead_source_analysis(company, from_date, to_date)` — leads by source with pie chart
- `get_sales_funnel(company, from_date, to_date)` — lead → opportunity → quotation → order pipeline
- Existing tools (`get_lead_statistics`, `get_opportunity_pipeline`) updated with ECharts

### 5.3 Settings ✅

- `enable_hrms_tools` flag in Chatbot Settings, conditional on HRMS module installation

---

## Phase 5A: UX & Accessibility ✅

**Goal:** Enhance the chat interface with file upload, voice communication, @mention autocomplete, prompt suggestions, and collapsible sidebar. Mix of backend and frontend changes.

### 5A.1 File Upload & Vision API ✅

**New file:** `ai_chatbot/api/files.py`
**Modified:** `api/chat.py`, `api/streaming.py`, `utils/ai_providers.py`, `frontend/src/utils/api.js`

- **Upload endpoint:** `upload_chat_file()` — validates ownership, MIME type (images, PDF, DOCX, CSV, XLSX, TXT), 10MB limit, saves to Frappe File DocType
- **Vision API support:** Image attachments sent to OpenAI/Claude Vision for analysis
  - OpenAI format as canonical internal representation (`image_url` content parts)
  - Claude provider converts to Claude's `image` + `base64` source format in `_convert_messages_to_claude()`
- **Upload-then-send (two-phase):** Files uploaded first to Frappe, metadata (not binary) passed with message — works with streaming's `frappe.enqueue`
- **Frontend composable:** `useFileUpload.js` — file selection, validation, preview URLs, pending file management
- **ChatInput UI:** Paperclip button, file chips with preview thumbnails, drag-and-drop overlay, max 5 files

### 5A.2 Voice Communication ✅

**New files:** `frontend/src/composables/useVoiceInput.js`, `frontend/src/composables/useVoiceOutput.js`
**Modified:** `frontend/src/components/ChatInput.vue`, `frontend/src/pages/ChatView.vue`, `frontend/src/components/ChatMessage.vue`

**Speech-to-Text (input):**
- `useVoiceInput.js` composable using Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`)
- `continuous=true`, `interimResults=true`, `lang=navigator.language`
- Microphone button with pulsing red animation when recording (`animate-recording`)
- Interim transcript displayed in real-time below input text
- Graceful degradation: mic button hidden in unsupported browsers (Firefox)

**Text-to-Speech (output):**
- `useVoiceOutput.js` composable using `SpeechSynthesis` API
- Markdown stripped before speaking (headers, bold, code, images, links, tables)
- **Auto-speak:** When user submits via voice, AI response auto-speaks after streaming completes
- **Manual "Listen" button** on all assistant messages (Volume2/VolumeX icons)

### 5A.3 @Mention Autocomplete & Prompt Suggestions ✅

**Backend:** `get_mention_values()` endpoint in `api/chat.py`
**Frontend:** Built into `ChatInput.vue` (no separate component needed)

**@Mention Autocomplete (8 categories):**
- `@company` → inserts user's default company name
- `@period` → sub-menu: "This Week", "This Month", "Last Month", "This Quarter", "This FY", "Last FY"
- `@cost_center` → searches cost centers (company-scoped)
- `@department` → searches departments (company-scoped)
- `@warehouse` → searches warehouses (company-scoped)
- `@customer` → searches customers
- `@item` → searches items
- `@accounting_dimension` → dynamically discovers active accounting dimensions via ERPNext's `get_accounting_dimensions()` API

**Implementation details:**
- Two-level drill-down: categories → values (fetched from backend)
- Keyboard navigation (arrow keys, Enter to select, Escape to close)
- Dropdown positioned above textarea
- Triggered on `@` at start of input or after whitespace

**Prompt Suggestions:**
- 4 default suggestion chips shown for new conversations (no messages)
- Click auto-inserts and sends
- Hidden after first message

### 5A.4 Collapsible Sidebar ✅

**Modified:** `ChatView.vue`, `ChatHeader.vue`

- `PanelLeftClose`/`PanelLeftOpen` toggle button in ChatHeader
- `sidebarCollapsed` state persisted in `localStorage` (`ai_chatbot_sidebar`)
- Vue `<transition>` with width + opacity animation
- Chat area expands to full width when sidebar collapsed

### 5A.5 Deliverables

| Item | Files | Status |
|------|-------|--------|
| File upload API | `api/files.py` (new) | ✅ |
| Attachments in chat/streaming | Updated `api/chat.py`, `api/streaming.py` | ✅ |
| Multimodal AI providers | Updated `utils/ai_providers.py` | ✅ |
| File upload composable | `composables/useFileUpload.js` (new) | ✅ |
| Voice input composable | `composables/useVoiceInput.js` (new) | ✅ |
| Voice output composable | `composables/useVoiceOutput.js` (new) | ✅ |
| API client updates | Updated `utils/api.js` (uploadFile, getMentionValues) | ✅ |
| ChatInput rewrite | Updated `components/ChatInput.vue` (file, voice, @mentions, suggestions) | ✅ |
| @Mention backend | `get_mention_values()` in `api/chat.py` | ✅ |
| ChatView orchestrator | Updated `pages/ChatView.vue` (payload, upload, voice, sidebar) | ✅ |
| ChatMessage updates | Updated `components/ChatMessage.vue` (attachments, speaker) | ✅ |
| Sidebar toggle | Updated `components/ChatHeader.vue` | ✅ |
| Tailwind animations | Updated `tailwind.config.js` (recording pulse) | ✅ |

**New dependencies:** None (Web Speech API, File API, SpeechSynthesis are browser-native).

---

## Phase 5B: Enterprise Analytics & Configuration ✅

**Goal:** Make the chatbot enterprise-ready with Frappe permissions, accounting dimensions, report integration, CFO-level reporting, parent company consolidation, configurable prompts, configurable constants, and plugin extensibility.

### 5B.1 User Permission Enforcement ✅

**Files:** `ai_chatbot/tools/registry.py`, tool module files

**Architecture:**
- Each `@register_tool` decorator declares which DocTypes the tool accesses:
  ```python
  @register_tool(
      name="get_sales_analytics",
      category="selling",
      description="...",
      parameters={...},
      doctypes=["Sales Invoice"],  # NEW: declares accessed doctypes
  )
  ```
- `registry.py`'s `execute_tool()` checks permission before calling the function:
  ```python
  from frappe.permissions import has_permission

  for dt in tool_info.get("doctypes", []):
      if not has_permission(dt, "read", user=frappe.session.user):
          return {"success": False, "error": f"No permission to read {dt}"}
  ```
- For report-based tools (Phase 5B.3), check `has_permission(report_name, "report")`
- Permission errors return a clear message the AI can relay to the user
- The system prompt dynamically lists only the tools the current user has permission to use

**Reference:** `from frappe.permissions import has_permission` — [Frappe Permission Docs](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)

### 5B.2 Accounting Dimensions ✅

**Files:** `ai_chatbot/core/dimensions.py` (new), updated finance tools, updated `prompts.py`

**Discovery:**
```python
# ai_chatbot/core/dimensions.py
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
    get_dimension_with_children,
)

def get_available_dimensions():
    """Get all active accounting dimensions for the current site."""
    dimensions = get_accounting_dimensions()
    return [{"fieldname": d.fieldname, "label": d.label, "document_type": d.document_type}
            for d in dimensions]

def get_dimension_values(dimension_doctype, company=None):
    """Get all valid values for a dimension (e.g., all Cost Centers)."""
    filters = {"company": company} if company else {}
    return frappe.get_all(dimension_doctype, filters=filters, pluck="name")

def get_dimension_with_children_safe(dimension_doctype, value):
    """Get dimension value including all children (for tree structures like Cost Center)."""
    return get_dimension_with_children(dimension_doctype, value)
```

**Tool Integration:**
- Finance tools (`receivables.py`, `payables.py`, `profitability.py`, `budget.py`, etc.) accept dynamic dimension parameters
- Common pattern:
  ```python
  @register_tool(
      name="get_receivable_aging",
      ...
      parameters={
          ...,
          "cost_center": {"type": "string", "description": "Filter by Cost Center"},
          "department": {"type": "string", "description": "Filter by Department"},
          "project": {"type": "string", "description": "Filter by Project"},
      },
  )
  def get_receivable_aging(..., cost_center=None, department=None, project=None):
      ...
      # Apply dimension filters dynamically
      for dim_field, dim_value in [("cost_center", cost_center), ("department", department), ("project", project)]:
          if dim_value:
              query = query.where(table[dim_field] == dim_value)
  ```
- A shared helper `apply_dimension_filters(query, table, **dimensions)` avoids repetition
- System prompt includes available dimensions so the AI knows to ask or suggest them

**Reference:** `from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions` — [ERPNext Accounting Dimensions](https://docs.frappe.io/erpnext/user/manual/en/accounting-dimensions)

### 5B.3 Report Data for Analysis

**Files:** `ai_chatbot/tools/reports.py` (new), `ai_chatbot/core/constants.py` (updated)

**Architecture:**
- Generic tool that executes any Frappe/ERPNext report and returns the result:
  ```python
  @register_tool(
      name="get_report_data",
      category="reports",
      description="Fetch data from any ERPNext report for analysis",
      parameters={
          "report_name": {"type": "string", "description": "Name of the report (e.g., 'General Ledger', 'Accounts Receivable')"},
          "filters": {"type": "object", "description": "Report filters as key-value pairs"},
      },
      doctypes=[],  # Permission checked per-report
  )
  def get_report_data(report_name, filters=None):
      # Check report permission
      if not frappe.has_permission("Report", report_name, "read"):
          return {"error": "No permission to access this report"}

      result = frappe.get_report_result(report_name, filters=filters or {})
      return {
          "columns": result.get("columns", []),
          "data": result.get("result", [])[:100],  # Limit rows for context window
          "report_name": report_name,
          "filters_used": filters,
      }
  ```
- Pre-configured report shortcuts for common analyses:
  - `get_general_ledger(from_date, to_date, account=None, company=None)`
  - `get_trial_balance(from_date, to_date, company=None)`
  - `get_profit_and_loss(from_date, to_date, company=None)`
  - `get_balance_sheet(date, company=None)`
  - `get_accounts_receivable_report(company=None, ageing_based_on="Due Date")`
- **Data consistency guarantee:** AI analysis is based on the same data the user sees in ERPNext reports
- Add `enable_report_tools` to TOOL_CATEGORIES in constants.py

### 5B.4 CFO Reporting (Composite Analysis) ✅

**Files:** `ai_chatbot/tools/finance/cfo.py` (new)

**Architecture:**
- Composite tools that call multiple existing tools and aggregate results:
  ```python
  @register_tool(
      name="get_cfo_dashboard",
      category="finance",
      description="Comprehensive financial dashboard with P&L, cash flow, ratios, and receivables/payables overview",
      parameters={
          "from_date": {"type": "string", "description": "Start date. Defaults to fiscal year start."},
          "to_date": {"type": "string", "description": "End date. Defaults to fiscal year end."},
          "company": {"type": "string", "description": "Company. Defaults to user's default company."},
      },
  )
  def get_cfo_dashboard(from_date=None, to_date=None, company=None):
      """Aggregates: P&L summary, cash flow, key ratios, AR/AP aging, budget variance."""
      ...
      return {
          "summary": { ... },
          "charts": [pl_chart, cashflow_chart, aging_chart, budget_chart],
          "tables": [ratios_table, top_debtors_table],
          ...
      }
  ```
- Additional CFO-level tools:
  - `get_financial_overview(company, period)` — high-level KPIs: revenue, expenses, net profit, cash position, AR, AP
  - `get_monthly_comparison(company, months=3)` — month-over-month comparison with variance
  - `get_year_over_year(company)` — YoY comparison of key metrics
- All return multiple charts via `charts` array (rendered by Phase 5A.4's multi-chart frontend)

### 5B.5 Parent Company / Multi-Company Consolidation ✅

**Files:** `ai_chatbot/core/config.py` (updated), `ai_chatbot/core/consolidation.py` (new), updated `prompts.py`

**Discovery:**
```python
# ai_chatbot/core/consolidation.py
def is_parent_company(company):
    """Check if a company has child companies."""
    return bool(frappe.db.get_descendants("Company", company))

def get_child_companies(parent_company):
    """Get all descendant companies."""
    return frappe.db.get_descendants("Company", parent_company)

def get_consolidated_data(tool_func, companies, target_currency, **kwargs):
    """Execute a tool across multiple companies and consolidate results.

    Converts all amounts to target_currency using exchange rates.
    """
    from ai_chatbot.data.currency import get_exchange_rate

    consolidated = []
    for company in companies:
        result = tool_func(company=company, **kwargs)
        company_currency = frappe.get_cached_value("Company", company, "default_currency")
        if company_currency != target_currency:
            rate = get_exchange_rate(company_currency, target_currency)
            result = _convert_amounts(result, rate)
        consolidated.append({"company": company, "data": result})

    return consolidated
```

**System Prompt Integration:**
- Detect if user's default company is a parent company
- Include in system prompt:
  ```
  ## Multi-Company Context
  - Your company "{company}" is a parent company with subsidiaries: {child_list}
  - When the user asks for consolidated data, ask them:
    1. Whether to include child companies
    2. Which currency to display (parent company currency or specific currency)
  - Use consolidation tools to aggregate across companies
  ```

**Flow:**
1. User asks "Show total sales" → AI sees parent company context in system prompt
2. AI asks: "Your company has subsidiaries: X, Y, Z. Would you like consolidated data or just {parent_company}?"
3. If consolidated → "In which currency? {parent_currency} or another?"
4. AI calls tool with `consolidated=True, currency=target_currency`
5. Tool iterates child companies, converts, aggregates

### 5B.6 Configurable System & User Prompts ✅

**Files:** `ai_chatbot/chatbot/doctype/chatbot_settings/chatbot_settings.json` (updated), `ai_chatbot/core/prompts.py` (updated)

**Chatbot Settings additions:**
- `custom_system_prompt` (Text Editor) — admin-defined system prompt additions
- `ai_persona` (Small Text) — customizable persona description (default: "intelligent ERPNext business assistant")
- `response_language` (Select) — preferred response language (English, Hindi, etc.)
- `custom_instructions` (Text Editor) — additional behavioral instructions appended to system prompt

**Prompt Builder update:**
```python
def build_system_prompt():
    settings = frappe.get_single("Chatbot Settings")

    # Use custom persona or default
    persona = settings.ai_persona or "an intelligent ERPNext business assistant"
    parts.append(f"You are {persona}. ...")

    # Append custom system prompt if configured
    if settings.custom_system_prompt:
        parts.append(f"\n## Custom Instructions\n{settings.custom_system_prompt}")

    # Response language
    if settings.response_language and settings.response_language != "English":
        parts.append(f"\n## Language\nRespond in {settings.response_language}.")

    ...
```

### 5B.7 Configurable Constants ✅

**Files:** `ai_chatbot/chatbot/doctype/chatbot_settings/chatbot_settings.json` (updated), `ai_chatbot/core/constants.py` (updated), `ai_chatbot/core/config.py` (updated)

**Move user-facing constants to Chatbot Settings:**

| Constant | Current Location | Move To |
|---|---|---|
| `DEFAULT_QUERY_LIMIT` (20) | `constants.py` | Settings: `default_query_limit` (Int) |
| `DEFAULT_TOP_N_LIMIT` (10) | `constants.py` | Settings: `default_top_n_limit` (Int) |
| `MAX_QUERY_LIMIT` (100) | `constants.py` | Settings: `max_query_limit` (Int) |
| Aging buckets | `constants.py` | Settings: `aging_buckets` (JSON) |
| Prompt suggestions | — | Settings: `prompt_suggestions` (JSON) |

**Keep in code (not user-configurable):**
- `BASE_AMOUNT_FIELDS` — technical field mapping
- `TRANSACTION_AMOUNT_FIELDS` — technical field mapping
- `TOOL_CATEGORIES` — tied to settings flags
- `LOG_TITLE` — internal logging
- `DATE_FORMAT` — standardized format

**Config helpers:**
```python
# ai_chatbot/core/config.py
def get_query_limit(requested=None):
    """Get query limit, capped at max."""
    settings = get_chatbot_settings()
    max_limit = settings.max_query_limit or 100
    default = settings.default_query_limit or 20
    return min(requested or default, max_limit)
```

### 5B.8 Tools as Plugins (External App Registration) ✅

**Files:** `ai_chatbot/hooks.py` (updated), `ai_chatbot/tools/registry.py` (updated)

**Hook-based tool registration:**
```python
# In hooks.py — define the hook
ai_chatbot_tool_modules = []  # Default empty, other apps extend this

# In registry.py — load external tools
def _ensure_tools_loaded():
    if _TOOL_REGISTRY:
        return

    # Load built-in tools
    import ai_chatbot.tools.crm
    import ai_chatbot.tools.selling
    ...

    # Load external plugin tools via Frappe hooks
    for module_path in frappe.get_hooks("ai_chatbot_tool_modules"):
        try:
            frappe.get_module(module_path)
        except Exception as e:
            frappe.log_error(f"Failed to load tool plugin: {module_path}: {e}", "AI Chatbot")
```

**How external apps register tools:**
```python
# In another_app/hooks.py
ai_chatbot_tool_modules = [
    "another_app.chatbot_tools.manufacturing",
    "another_app.chatbot_tools.quality",
]

# In another_app/chatbot_tools/manufacturing.py
from ai_chatbot.tools.registry import register_tool

@register_tool(
    name="get_production_summary",
    category="manufacturing",
    description="Get production order summary",
    parameters={...},
    doctypes=["Work Order"],
)
def get_production_summary(company=None):
    ...
```

**TOOL_CATEGORIES update:**
- Dynamic category registration: external apps can declare new categories
- `TOOL_CATEGORIES` becomes a function that merges built-in + hook-defined categories

### 5B.9 Deliverables

| Item | Files |
|------|-------|
| Permissions | Updated `tools/registry.py`, all tool decorators |
| Dimensions | `core/dimensions.py`, updated finance tools, updated `prompts.py` |
| Reports | `tools/reports.py` (new) |
| CFO reporting | `tools/finance/cfo.py` (new) |
| Consolidation | `core/consolidation.py` (new), updated `config.py`, `prompts.py` |
| Configurable prompts | Updated Chatbot Settings DocType, updated `prompts.py` |
| Configurable constants | Updated Chatbot Settings DocType, updated `config.py`, `constants.py` |
| Plugin system | Updated `hooks.py`, updated `registry.py` |

**New dependencies:** None (uses Frappe built-ins and ERPNext APIs).

---

## Phase 6: Settings Overhaul, Gemini Provider & Token Optimization ✅

**Goal:** Simplify AI provider configuration with a single-provider dropdown (OpenAI/Claude/Gemini), add Gemini as a third provider, implement token/cost tracking, optimize token usage, tailor financial analysis behaviour, add source file headers, and reorganize Chatbot Settings into tabs.

### 6.1 Chatbot Settings Overhaul ✅

**Files:** `chatbot_settings.json`, `ai_providers.py`, `api/chat.py`, `api/streaming.py`

**Current state:** Separate "OpenAI Configuration" and "Claude Configuration" sections with independent enabled flags, API keys, models, temperature, and max tokens.

**Target state:** Single provider selection with dynamic fields:

```
┌─────────────────────────────────────────────────────┐
│ Tab: API Configuration                              │
├─────────────────────────────────────────────────────┤
│ AI Provider: [OpenAI ▼]  [Claude]  [Gemini]         │
│                                                     │
│ API Key:       [••••••••••••••••••]                  │
│ Model:         [claude-opus-4-5-20251101 ▼]         │
│ Temperature:   [0.7]                                │
│ Max Tokens:    [4000]                               │
├─────────────────────────────────────────────────────┤
│ Tab: Tools                                          │
├─────────────────────────────────────────────────────┤
│ ☑ CRM Tools  ☑ Sales Tools  ☑ Purchase Tools       │
│ ☑ Finance Tools  ☑ Inventory Tools  ☑ HRMS Tools   │
│ ☑ Write Operations                                  │
├─────────────────────────────────────────────────────┤
│ Tab: Query Configuration                            │
├─────────────────────────────────────────────────────┤
│ Default Query Limit: [20]  Max Query Limit: [100]   │
│ Default Top-N Limit: [10]                           │
├─────────────────────────────────────────────────────┤
│ Tab: Prompts                                        │
├─────────────────────────────────────────────────────┤
│ AI Persona:        [...]                            │
│ Response Language:  [English ▼]                     │
│ Custom System Prompt: [...]                         │
│ Custom Instructions:  [...]                         │
├─────────────────────────────────────────────────────┤
│ Tab: Streaming                                      │
├─────────────────────────────────────────────────────┤
│ ☑ Enable Streaming                                  │
└─────────────────────────────────────────────────────┘
```

**Fields to add/change:**
- Replace `openai_enabled`, `claude_enabled` with single `ai_provider` (Select: OpenAI/Claude/Gemini)
- Replace provider-specific API key, model, temperature, max_tokens with unified fields: `api_key` (Password), `model` (Data), `temperature` (Float, default 0.7), `max_tokens` (Int, default 4000)
- Add `max_chat_history` (Int, default 10) — limits sidebar conversation list
- Add Tab Breaks: "API Configuration", "Tools", "Query Configuration", "Prompts", "Streaming"
- Model defaults per provider: OpenAI → `gpt-4o`, Claude → `claude-opus-4-5-20251101`, Gemini → `gemini-2.5-flash`

**Migration:** Data migration script to move existing OpenAI/Claude settings to the unified fields.

### 6.2 Gemini Provider ✅

**Files:** `utils/ai_providers.py`

**Approach:** Use Google's OpenAI-compatible endpoint — the existing `OpenAIProvider` class can be extended with minimal changes since Gemini's OpenAI-compat endpoint uses the same request/response format for chat completions, tool calling, and streaming.

```python
class GeminiProvider(OpenAIProvider):
    """Google Gemini provider via OpenAI-compatible endpoint."""

    def __init__(self, settings):
        self.api_key = settings.api_key
        self.model = settings.model or "gemini-2.5-flash"
        self.temperature = settings.temperature or 1.0
        self.max_tokens = settings.max_tokens or 8192
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
```

**Available models:**
- `gemini-2.5-flash` (default — fast, cost-effective)
- `gemini-2.5-pro` (premium reasoning)
- `gemini-2.5-flash-lite` (budget)

**Multimodal:** Gemini supports vision natively via the OpenAI-compat endpoint — image_url format works as-is.

**No new Python dependency required** — uses existing `requests` library via the OpenAI-compatible REST API.

### 6.3 AI Behaviour for Finance Prompts ✅

**Files:** `core/prompts.py`

Add a dedicated "Financial Analyst / CFO" behaviour section to the system prompt when finance tools are enabled:

```python
if is_tool_category_enabled("enable_finance_tools"):
    parts.append(
        "\n## Financial Analysis Behaviour\n"
        "When answering financial questions, act as a seasoned Financial Analyst / CFO:\n"
        "- Provide context for numbers (YoY change, % of revenue, industry benchmarks)\n"
        "- Highlight key risks and opportunities in the data\n"
        "- Suggest actionable next steps when presenting financial metrics\n"
        "- Use professional financial terminology (EBITDA, DSO, working capital cycle)\n"
        "- Compare current metrics against previous periods when data is available\n"
        "- Flag anomalies or concerning trends proactively"
    )
```

### 6.4 Token Optimization ✅

**Files:** `core/token_optimizer.py` (new), updated `api/chat.py`, `api/streaming.py`

**Strategies:**
1. **Conversation history trimming** — keep only the last N messages in context (configurable via `max_context_messages` in settings, default 20)
2. **Tool result compression** — strip verbose metadata from tool responses before including in context; keep only the data the AI needs
3. **Structured data extraction** — when tool results contain large datasets, summarize to key metrics before including in context
4. **System prompt caching** — cache the system prompt per-user and only rebuild when settings change

```python
# ai_chatbot/core/token_optimizer.py
def trim_conversation_history(messages, max_messages=20):
    """Keep system prompt + last N messages."""
    system = [m for m in messages if m["role"] == "system"]
    history = [m for m in messages if m["role"] != "system"]
    return system + history[-max_messages:]

def compress_tool_result(result, max_rows=20):
    """Compress tool results to reduce token usage."""
    if isinstance(result.get("data"), list) and len(result["data"]) > max_rows:
        result["data"] = result["data"][:max_rows]
        result["_truncated"] = True
        result["_total_rows"] = len(result["data"])
    # Remove echart_option from context (frontend renders it, AI doesn't need it)
    result.pop("echart_option", None)
    return result
```

### 6.5 Cost Monitoring & Analytics ✅

**Files:** `chatbot/doctype/chatbot_token_usage/` (new DocType), `core/token_tracker.py` (new), updated `api/chat.py`

**Chatbot Token Usage** DocType:
- `user` (Link: User)
- `conversation` (Link: Chatbot Conversation)
- `provider` (Data) — OpenAI/Claude/Gemini
- `model` (Data) — specific model used
- `prompt_tokens` (Int)
- `completion_tokens` (Int)
- `total_tokens` (Int)
- `estimated_cost` (Currency) — calculated from token counts × model pricing
- `date` (Date)

**Token tracker middleware:**
```python
# ai_chatbot/core/token_tracker.py
def track_token_usage(provider, model, prompt_tokens, completion_tokens, user, conversation_id):
    """Record token usage for cost tracking."""
    cost = estimate_cost(provider, model, prompt_tokens, completion_tokens)
    frappe.get_doc({
        "doctype": "Chatbot Token Usage",
        "user": user,
        "conversation": conversation_id,
        "provider": provider,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "estimated_cost": cost,
        "date": frappe.utils.today(),
    }).insert(ignore_permissions=True)

MODEL_PRICING = {
    # Per 1M tokens: (input, output)
    "gpt-4o": (2.50, 10.00),
    "claude-opus-4-5-20251101": (15.00, 75.00),
    "claude-sonnet-4-5-20250929": (3.00, 15.00),
    "gemini-2.5-flash": (0.15, 0.60),
    "gemini-2.5-pro": (1.25, 10.00),
}
```

**Monthly analytics tool** — registered as a chatbot tool so users can ask "How much have I spent on AI this month?":
```python
@register_tool(name="get_ai_usage_analytics", ...)
def get_ai_usage_analytics(from_date=None, to_date=None):
    """Get token usage and cost analytics."""
```

**Alerting:** Configurable monthly budget threshold in Chatbot Settings. When exceeded, log a warning and optionally notify the admin.

### 6.6 Source File Header Policy ✅

**Files:** All `.py`, `.js`, and `.vue` files in the project

Every Python, JavaScript, and Vue source file has been prepended with:
```python
# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
```
```javascript
// Copyright (c) 2026, Sanjay Kumar and contributors
// For license information, please see license.txt
```
```html
<!-- Copyright (c) 2026, Sanjay Kumar and contributors -->
<!-- For license information, please see license.txt -->
```

65 files updated across Python, JavaScript, and Vue source files.

### 6.7 Deliverables ✅

| Item | Files |
|------|-------|
| Settings overhaul | Updated `chatbot_settings.json` (tabs, unified provider) |
| Gemini provider | Updated `ai_providers.py` (GeminiProvider class) |
| Finance AI behaviour | Updated `prompts.py` |
| Token optimization | `core/token_optimizer.py` (new) |
| Cost monitoring | `chatbot/doctype/chatbot_token_usage/` (new), `core/token_tracker.py` (new) |
| Source headers | All `.py` and `.js` files |

**New dependencies:** None (Gemini uses OpenAI-compatible REST API via `requests`).

---

## Phase 6A: UI Overhaul ✅

**Goal:** Redesign the chatbot UI for a cleaner, more professional look — remove header, redesign sidebar (Claude.AI-style), add real-time process indicators, greeting, search, proper alignment, and OS dark mode support.

### 6A.1 Header Removal & Sidebar Redesign ✅

**Files:** `ChatView.vue` (major rewrite), `Sidebar.vue` (complete rewrite), `ChatHeader.vue` (deleted)

- **Header removed entirely** — provider selector, settings gear, and sidebar toggle all moved to sidebar
- **Sidebar redesigned** (Claude.AI-inspired):
  - **Expanded mode (w-72):** Header row (hamburger toggle + logo + settings gear), grey "New Chat" button, search input with debounce, date-grouped conversations (Today/Yesterday/Last 7 Days/Older), provider selector dropdown at bottom
  - **Collapsed mode (w-14):** Icon-only strip — expand button, new chat (+), search icon
  - Sidebar always visible (collapse = icon strip, expand = full panel) — no more hide/show
  - `sidebarCollapsed` state persisted in `localStorage`
- **ChatView wiring:** Sidebar receives `:selected-provider`, `:sidebar-collapsed`, `:search-results`, `:is-searching` props; emits `@toggle-sidebar`, `@change-provider`, `@search`

### 6A.2 Remove Prompt Suggestions ✅

**Files:** `ChatInput.vue`

- Removed `suggestions` array, `handleSuggestionClick`, suggestion template block, `showSuggestions` prop
- Removed `Zap` icon import (was only used in hints bar)

### 6A.3 Send/Stop Button & Input Cleanup ✅

**Files:** `ChatInput.vue`

- **Send button:** Icon-only (`<Send :size="18" />`), 52×52px square, blue, `title="Send message"`
- **Stop button:** Icon-only (`<Square :size="16" />`), 52×52px square, red, `title="Stop generating"`
- **Hints bar removed** — no more "ERPNext tools enabled", "Voice input", "Press Enter to send"
- Layout: paperclip | textarea | mic | send/stop

### 6A.4 Personalized Greeting ✅ (Pre-Phase 6A)

**Files:** `ChatView.vue`

- When `hasNoMessages`: centered logo + "Hello, {UserFullName}!" + "How can I help you today?" + centered ChatInput
- Once a message is sent: normal bottom-pinned layout

### 6A.5 Chat Search ✅

**Files:** `api/chat.py` (new endpoint), `utils/api.js`, `Sidebar.vue`, `ChatView.vue`

- **Backend:** `search_conversations(query, limit=20)` — searches `Chatbot Conversation.title` and `Chatbot Message.content` using `LIKE %query%`, filters by current user, returns deduplicated results ordered by `updated_at desc`
- **Frontend API:** `chatAPI.searchConversations(query, limit)` method
- **Sidebar:** When search query is active, results replace grouped conversation list; "No results" empty state; clicking a result loads conversation and clears search
- **Debounce:** 300ms in Sidebar before emitting `@search` to ChatView

### 6A.6 Response Panel Width ✅

**Files:** `ChatMessage.vue`, `ChatView.vue`

- **Assistant messages:** `max-w-[85%] lg:max-w-5xl` (was `max-w-3xl`)
- **User messages:** `max-w-3xl` (unchanged)
- **Streaming bubble:** Same wider width as assistant messages
- Tables, charts, and code blocks now use the full available response width

### 6A.7 Dark Mode ✅

**Files:** `tailwind.config.js`, `App.vue`, `ChatMessage.vue`, `ChatInput.vue`, `Sidebar.vue`, `TypingIndicator.vue`, `ChatView.vue`

- **Tailwind:** `darkMode: 'class'` configuration
- **App.vue:** Detects `prefers-color-scheme: dark` on mount, toggles `dark` class on `<html>`, listens for OS theme changes; background changed from gradient to `bg-white dark:bg-gray-900`
- **Dark scrollbars:** Custom scrollbar colors for dark mode
- **Dark markdown:** Global CSS overrides for `.dark .markdown-body` (text, code, links, blockquotes, tables)
- **All components:** `dark:` variant classes on backgrounds, borders, text colors, hover states
- **Scoped styles:** ChatMessage.vue has dark mode overrides for `.markdown-body` elements

### 6A.8 Real-Time Process Indicators ✅

**Files:** `api/streaming.py`, `composables/useStreaming.js`, `TypingIndicator.vue`, `ChatView.vue`

**Backend (`streaming.py`):**
- New `_publish_process_step(conversation_id, stream_id, step, user)` helper
- Process steps published at 5 pipeline points:
  1. After stream start: `"Preparing context..."`
  2. Before provider call: `"Communicating with LLM..."`
  3. Before each tool execution: `"Executing {Tool Name}..."`
  4. After tool results: `"Processing results..."`
  5. Before saving: `"Saving response..."`

**Frontend (`useStreaming.js`):**
- New `processStep` ref (readonly)
- `ai_chat_process_step` event handler updates `processStep.value`
- Cleared in `reset()` and `startListening()`

**TypingIndicator.vue:**
- Accepts `processStep` prop
- Displays `{{ processStep || 'AI is thinking...' }}`
- Logo SVG replaces hardcoded "AI" text avatar
- Dark mode text color

**ChatView.vue:**
- Destructures `processStep` from `useStreaming()`
- Passes `:process-step="processStep"` to TypingIndicator
- Shows process step during streaming above content

### 6A.9 Logo, Favicon & User Avatar ✅

**Files:** `frontend/src/assets/logo.svg`, `frontend/public/favicon.svg`, `ChatMessage.vue`, `ChatView.vue`, `Sidebar.vue`, `TypingIndicator.vue`

- Custom orbital SVG (violet gradient, RGB dots, chat bubble tail) as favicon and logo
- Logo displayed in sidebar header, AI messages, streaming messages, and typing indicator
- User avatar on right side of user message bubbles with initials fallback

### 6A.10 Deliverables ✅

| Item | Files | Status |
|------|-------|--------|
| Header removal | Deleted `ChatHeader.vue` | ✅ |
| Sidebar redesign | Complete rewrite of `Sidebar.vue` (Claude.AI style, search, collapse, date groups, provider) | ✅ |
| Layout | Major rewrite of `ChatView.vue` (no header, greeting, wider messages, process steps) | ✅ |
| Process indicators | Updated `TypingIndicator.vue` + `streaming.py` + `useStreaming.js` | ✅ |
| Send/Stop icons | Updated `ChatInput.vue` (icon-only, no suggestions, no hints) | ✅ |
| Chat search | `search_conversations()` endpoint + `searchConversations()` API + sidebar search UI | ✅ |
| Dark mode | `tailwind.config.js`, `App.vue`, all components with `dark:` variants | ✅ |
| Response width | `ChatMessage.vue` wider assistant messages (`max-w-[85%] lg:max-w-5xl`) | ✅ |

**New dependencies:** None.

---

## Phase 6B: Multi-Dimensional Analytics & GL-Based Finance ✅

**Goal:** Support multi-dimensional/hierarchical data grouping across dimensions and time periods, enhance finance tools with GL Entry-based queries for authoritative accounting data, add BI metric cards to CFO dashboard, and UI refinements.

### 6B.1 Multi-Dimensional Data Grouping Tool ✅

**Files:** `tools/finance/analytics.py` (new), `data/grouping.py` (new)

**Architecture:**
- **Grouping engine** (`data/grouping.py`): `METRIC_CONFIG` maps metrics to doctypes/fields; `DIMENSION_FIELDS` maps dimension names to doctype fields with optional child-table JOIN support; custom PyPika `Quarter(Function)` for MySQL `QUARTER()`.
- **Built-in dimensions:** `territory`, `customer_group`, `customer`, `item_group`, `cost_center`, `department`.
- **Accounting Dimensions:** Any Accounting Dimension created in ERPNext (e.g. `business_vertical`, `business_segment`, `project`) is automatically discovered via `get_accounting_dimensions()` and available for grouping. The tool validates that the dimension field actually exists on the target doctype before querying (`_validate_dimension_on_doctype()` uses `frappe.get_meta().has_field()`). `get_all_dimensions()` merges built-in + accounting dimensions at runtime.
- **Supported metrics:** `revenue` (Sales Invoice), `expenses` (Purchase Invoice), `profit` (computed: revenue - expenses), `orders` (Sales Order)
- **Hierarchical output:** `_pivot_to_hierarchical()` transforms flat SQL GROUP BY results into indented tree with group header rows and subtotals. Max 3 dimensions.
- **Stacked bar chart:** `data/charts.py` → `build_stacked_bar_chart()` with series stacking.

**Output format:**
```json
{
    "headers": ["Territory", "Total", "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"],
    "rows": [
        {"description": "India", "level": 0, "is_group": true, "values": [218.50, 45.00, 51.00, 57.50, 65.00]},
        {"description": "North", "level": 1, "is_group": false, "values": [120.00, 25.00, 28.00, 32.00, 35.00]},
        ...
    ]
}
```

**Frontend rendering:**
- `HierarchicalTable.vue`: Parent rows in bold with tinted background, child rows indented by level, values right-aligned with tabular-nums, overflow-x scroll for many period columns
- `BiCards.vue`: Responsive grid of metric cards with trend icons, YoY change percentages, abbreviated values (K/M)
- Stacked bar chart via existing `ChartMessage.vue` / `EChartRenderer.vue`

### 6B.2 GL Entry-Based Finance Queries ✅

**Files:** `tools/finance/gl_analytics.py` (new)

Three GL Entry-based tools using `frappe.qb` JOIN of `GL Entry` + `Account`:

1. **`get_gl_summary`** — GL Entry aggregation grouped by `root_type`, `account_type`, `party_type`, `voucher_type`, or `account_name`. Filters by root_type, account_type, date range, company. Returns bar/horizontal-bar chart.
2. **`get_trial_balance`** — Two-query approach (opening balance before from_date + period movement). Accounts grouped by root_type with subtotals and grand total.
3. **`get_account_statement`** — Opening balance + individual GL entries with running balance per row + line chart.

All tools filter `gle.is_cancelled == 0`, use `build_currency_response()`, declare doctypes `["GL Entry", "Account"]`.

### 6B.3 Enhanced CFO Dashboard with BI Cards ✅

**Files:** `tools/finance/cfo.py` (updated)

- `get_cfo_dashboard()` now computes YoY change for revenue and net profit by running prior-year queries
- Returns `bi_cards` array at top level of response:
  ```json
  {
      "bi_cards": [
          {"label": "Revenue", "value": 1250000, "change_pct": 12.5, "change_period": "YoY", "trend": "up", "icon": "trending-up"},
          {"label": "Net Profit", "value": 187500, "change_pct": -3.2, "change_period": "YoY", "trend": "down", "icon": "bar-chart-3"},
          {"label": "Cash Position", "value": 450000, "trend": "up", "icon": "wallet"},
          {"label": "AR Outstanding", "value": 320000, "trend": "flat", "icon": "arrow-up-right"},
          {"label": "AP Outstanding", "value": 180000, "trend": "flat", "icon": "arrow-down-right"}
      ],
      ...
  }
  ```

### 6B.4 UI Refinements ✅

**Sidebar header rearrangement:**
- **Before:** `[Toggle] [Logo] [Settings]` (symmetric layout)
- **After:** `[Logo (left)] ... [Settings] [Toggle (right)]` — logo anchored left, action buttons grouped right

**Personalized greeting:**
- **Before:** Centered app logo (orbital SVG) + "Hello, {name}!"
- **After:** Centered **user avatar** (large, 96×96px rounded) with initials fallback + "Hello, {name}!" — more personal

**Accounting Dimension auto-discovery:**
- `get_all_dimensions()` in `data/grouping.py` merges built-in dimensions with accounting dimensions discovered via `get_accounting_dimensions()`
- `_validate_dimension_on_doctype()` checks `frappe.get_meta().has_field()` before querying to ensure the field exists on the target doctype
- Tool description tells the AI to use exact fieldnames for accounting dimensions and that they are auto-discovered

**Query compatibility fix:**
- Replaced `fn.Year()` (not available in frappe.qb) with `fn.DateFormat(date, "%Y")` for quarterly period expressions
- Uses `fn.Quarter()` from frappe.qb instead of custom PyPika subclass

### 6B.5 Token Optimization ✅

- `token_optimizer.py` strips `hierarchical_table` and `bi_cards` from tool results in conversation history (frontend renders them; AI doesn't need them in context)

### 6B.6 Deliverables ✅

| Item | Files | Status |
|------|-------|--------|
| Grouping engine | `data/grouping.py` (new) | ✅ |
| Stacked bar chart | Updated `data/charts.py` (`build_stacked_bar_chart`) | ✅ |
| Multi-dimensional tool | `tools/finance/analytics.py` (new) | ✅ |
| GL Entry analytics | `tools/finance/gl_analytics.py` (new, 3 tools) | ✅ |
| CFO BI cards | Updated `tools/finance/cfo.py` (YoY queries + `bi_cards`) | ✅ |
| Tool registration | Updated `tools/registry.py` (imports analytics + gl_analytics) | ✅ |
| BI Cards component | `components/charts/BiCards.vue` (new) | ✅ |
| Hierarchical table | `components/charts/HierarchicalTable.vue` (new) | ✅ |
| ChatMessage integration | Updated `ChatMessage.vue` (renders bi_cards + hierarchical_table) | ✅ |
| Sidebar header | Updated `Sidebar.vue` (logo left, settings+toggle right) | ✅ |
| Greeting avatar | Updated `ChatView.vue` (user avatar replaces app logo) | ✅ |
| Token optimization | Updated `token_optimizer.py` (strips hierarchical_table, bi_cards) | ✅ |

**New dependencies:** None.

---

## Phase 6B+: Parent-Child Company Session Context, Fixes & Refinements ✅

**Goal:** Implement session-level parent-child company logic, session variables for subsidiary inclusion and target currency, fix BI card display issues, fix duplicate table rendering, add suffix/partial matching for dimension resolution, rename hierarchical table first column to "Particular", and add `company_label` with subsidiary notation across all tool responses.

### 6B+.1 Session Context Management ✅

**New files:** `core/session_context.py`, `tools/session.py`
**Modified:** `chatbot_conversation.json` (added `session_context` JSON field)

**Architecture:**
- `session_context` JSON field on Chatbot Conversation DocType stores per-conversation variables
- Two session variables:
  - `include_subsidiaries` (bool) — when True, all finance/analytics queries include child company data
  - `target_currency` (str | None) — display currency override (via @Currency or explicit user request)
- `get_session_context(conversation_id)` — reads from DB with defaults
- `set_session_context(conversation_id, key, value)` — updates single key
- `get_companies_for_query(company, conversation_id)` — returns `[parent, child1, child2, ...]` when subsidiaries enabled
- `get_display_currency(company, conversation_id)` — returns target currency or company default
- `build_company_label(company, conversation_id)` — returns `"Company Name"` or `"Company Name including its subsidiaries"`

**Session tools (AI-callable):**
- `set_include_subsidiaries(include)` — toggle subsidiary inclusion for the chat session
- `set_target_currency(currency)` — set/reset display currency for the chat session
- Both accessed via `frappe.flags.current_conversation_id` set in `chat.py` and `streaming.py`

### 6B+.2 Parent-Child Company Logic in All Tools ✅

**Modified:** `data/grouping.py`, `data/currency.py`, `api/chat.py`, `api/streaming.py`, and **all tool modules** (see below)

**Infrastructure:**
- `frappe.flags.current_conversation_id` set before tool execution in both chat and streaming paths
- `build_currency_response()` enhanced:
  - Adds `company_label` with subsidiary notation (uses `build_company_label()`)
  - Overrides `currency` if `target_currency` set in session
- New `build_company_context()` helper for non-monetary tools (counts, rates) — adds `company` + `company_label`
- `_build_and_run_query()` in grouping engine supports list of companies via `.isin()` filter
- `get_grouped_metric()` uses `get_companies_for_query()` to auto-include subsidiaries

**Complete `get_company_filter` migration across all tools:**

Every session-aware tool function replaced `get_default_company(company)` with `get_company_filter(company)` from `core/session_context.py`. This function returns either a single company string (normal) or a list of companies (when subsidiaries are enabled). All queries updated to handle both cases:
- `frappe.qb` queries: `isinstance(company, list)` → `.where(dt.company.isin(company))` vs `.where(dt.company == company)`
- `frappe.db.count` dict filters: `["in", company]` for lists
- `_primary(company)` helper added to each module for functions that require a single company (e.g., `get_fiscal_year_dates()`, `build_currency_response()`, `build_company_context()`)
- Files with many queries added `_apply_company_filter(query, doctype_ref, company)` helper to reduce repetition

| Module | Functions migrated |
|--------|-------------------|
| `tools/selling.py` | `get_sales_summary`, `get_top_customers`, `get_sales_by_item`, `get_sales_trend`, `get_sales_order_status` |
| `tools/buying.py` | `get_purchase_summary`, `get_top_suppliers`, `get_purchase_trend`, `get_purchase_orders_status` |
| `tools/stock.py` | `get_low_stock_items`, `get_stock_movement`, `get_stock_ageing`, `get_warehouse_summary` |
| `tools/account.py` | `get_profit_and_loss`, `get_balance_sheet` |
| `tools/crm.py` | `get_lead_statistics`, `get_opportunity_summary`, `get_lead_conversion_rate`, `get_lead_source_analysis`, `get_sales_funnel`, `get_opportunity_by_stage` |
| `tools/hrms.py` | `get_employee_count`, `get_attendance_summary`, `get_leave_balance`, `get_payroll_summary`, `get_department_wise_salary`, `get_employee_turnover` |
| `tools/finance/budget.py` | `get_budget_vs_actual`, `get_budget_variance` |
| `tools/finance/cash_flow.py` | `get_cash_flow_statement`, `get_cash_flow_trend`, `get_bank_balance` |
| `tools/finance/payables.py` | `get_payable_aging`, `get_top_creditors` |
| `tools/finance/receivables.py` | `get_receivable_aging`, `get_top_debtors` |
| `tools/finance/ratios.py` | `_get_current_assets_liabilities`, `get_liquidity_ratios`, `get_profitability_ratios`, `get_efficiency_ratios` |
| `tools/finance/working_capital.py` | `get_working_capital_summary`, `get_cash_conversion_cycle` |
| `tools/finance/profitability.py` | `get_profitability_by_customer`, `get_profitability_by_item`, `get_profitability_by_territory` |
| `tools/finance/gl_analytics.py` | `get_gl_summary`, `get_trial_balance`, `get_account_statement` |
| `tools/finance/cfo.py` | `get_financial_overview`, `get_cfo_dashboard`, `get_monthly_comparison` |

**Intentionally NOT migrated** (correct usage of `get_default_company`):
- `tools/consolidation.py` — has its own cross-company consolidation logic
- `tools/operations/search.py` — search doesn't need multi-company session awareness
- `tools/session.py` — session management tools define the context, not consume it
- `tools/finance/analytics.py` — `data/grouping.py` handles its own session context expansion internally

### 6B+.3 Company Label in All Tool Responses ✅

**Modified:** All tool modules — CRM, Stock, HRMS, Selling, Buying, Account, Finance

- Tools using `build_currency_response()` automatically get `company_label` (already handled by updated function)
- Tools that manually set `"company": company` converted to use `build_company_context()`:
  - CRM: `get_lead_statistics`, `get_lead_conversion_rate`, `get_lead_source_analysis`, `get_sales_funnel`
  - Stock: `get_low_stock_items`, `get_stock_movement`, `get_stock_ageing`
  - HRMS: `get_employee_count`, `get_attendance_summary`, `get_leave_balance`, `get_employee_turnover`
- System prompt updated: AI instructed to always mention company name using `company_label` field

### 6B+.4 Currency Logic for Company Grouping ✅

**Modified:** `core/prompts.py`

- When data is grouped by company and no target currency is set, AI instructed to show each company's data in its own default currency
- When target currency is set via session, all amounts shown in that currency
- System prompt updated with session variable management instructions

### 6B+.5 Dimension Name Resolution Enhancement ✅

**Modified:** `data/grouping.py` — `resolve_dimension_name()`

Added three new matching strategies (in priority order after existing exact/normalized/label match):
1. **Suffix match:** `"vertical"` → matches `"business_vertical"` (checks `key.endswith(f"_{normalized}")`)
2. **Label word match:** `"vertical"` → matches dimension with label containing "Vertical" as a word
3. **Contains match:** `"vertical"` → matches any key containing "vertical" as substring
All return a match only when exactly one candidate is found (avoids ambiguity).

### 6B+.6 BI Cards Display Fix ✅

**Modified:** `tools/finance/cfo.py`

- Added `bi_cards` to `get_financial_overview()` result (was previously only in `get_cfo_dashboard()`)
- Updated `get_cfo_dashboard()` description to explicitly mention BI cards and suggest it for dashboard/overview requests
- Cards: Revenue, Gross Profit (with margin %), Cash Position, Receivables, Payables

### 6B+.7 Duplicate Table Fix ✅

**Modified:** `frontend/src/components/ChatMessage.vue`

- When `hierarchicalTables` data is present, markdown tables are stripped from `renderedContent`
- Regex: removes `|...|` table blocks from rendered content when HierarchicalTable component will render the same data
- User sees only the compact, elegant HierarchicalTable component (after chart), not the AI's markdown table too

### 6B+.8 Hierarchical Table First Column ✅

**Modified:** `data/grouping.py`

- First column header changed from dimension label (e.g. "Territory") to `"Particular"` across all hierarchical table outputs
- Applied to both `get_grouped_metric()` and `_get_profit_grouped()` return headers

### 6B+.9 Deliverables ✅

| Item | Files | Status |
|------|-------|--------|
| Session context module | `core/session_context.py` (new) | ✅ |
| Session tools | `tools/session.py` (new) | ✅ |
| DocType update | Updated `chatbot_conversation.json` (`session_context` field) | ✅ |
| Conversation context flag | Updated `api/chat.py`, `api/streaming.py` | ✅ |
| Currency response enhancement | Updated `data/currency.py` (`build_currency_response`, `build_company_context`) | ✅ |
| Multi-company grouping | Updated `data/grouping.py` (list company filter, session context) | ✅ |
| Tool registration | Updated `tools/registry.py` (session tools import) | ✅ |
| `get_company_filter` migration | All 15 tool modules (51+ functions) → `get_company_filter` + multi-company queries | ✅ |
| CRM company labels | Updated `tools/crm.py` (6 tools → `get_company_filter` + `build_company_context`) | ✅ |
| Stock company labels | Updated `tools/stock.py` (4 tools → `get_company_filter` + `build_company_context`) | ✅ |
| HRMS company labels | Updated `tools/hrms.py` (6 tools → `get_company_filter` + `build_company_context`) | ✅ |
| Finance tools migration | All 9 finance modules → `get_company_filter` + multi-company queries | ✅ |
| Selling/Buying migration | Updated `tools/selling.py` (5 tools), `tools/buying.py` (4 tools) | ✅ |
| Account migration | Updated `tools/account.py` (2 tools) | ✅ |
| CFO BI cards fix | Updated `tools/finance/cfo.py` (bi_cards in financial_overview) | ✅ |
| System prompt | Updated `core/prompts.py` (session vars, company label, currency) | ✅ |
| Dimension resolution | Updated `data/grouping.py` (suffix/partial/contains matching) | ✅ |
| Duplicate table fix | Updated `ChatMessage.vue` (strip markdown tables when hierarchical) | ✅ |
| First column rename | Updated `data/grouping.py` (headers use "Particular") | ✅ |

**New dependencies:** None.

---

## Phase 6C: Workspace, Help & Language Selection

**Goal:** Create a Frappe workspace for desk access, add user help with sample prompts, move response language to the chat UI.

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

## Phase 7: Intelligent Document Processing (IDP) ✅

**Goal:** Extract structured data from uploaded documents (invoices, POs, receipts, quotations) using LLM Vision/text extraction and ERPNext schema discovery. Map non-uniform, multi-language source data to ERPNext DocType schemas with semantic reasoning. Create records and compare documents against existing ERPNext records.

### 7.1 Core Challenge

- Source data is non-uniform — inconsistent headers, varying formats, different languages
- LLM performs semantic reasoning to identify which source values map to which ERPNext fields
- Schema mapping resolves naming discrepancies between source document fields and ERPNext DocType structure
- All dates normalized to YYYY-MM-DD, all numbers stripped of currency symbols/commas
- Currency identified from document; `conversion_rate` defaults to 1.0 if not specified

### 7.2 File Upload Infrastructure (Completed in Phase 5A)

File upload and Vision API support was implemented in Phase 5A:
- `api/files.py` — upload endpoint, base64 encoding, vision content builder
- Frontend: file picker + drag-and-drop in ChatInput (accept PDF, images, Excel, CSV, DOCX, TXT)
- Frappe File DocType storage with `is_private=True`
- Image attachments sent to LLM Vision API (OpenAI, Claude & Gemini)

**Phase 7 extends this with:**
- PDF text extraction for prompt context (pypdf)
- Excel/CSV tabular data extraction (openpyxl + stdlib csv)
- DOCX text extraction (python-docx)
- Scanned PDF fallback to Vision API via base64

### 7.3 Content Extractors (`ai_chatbot/idp/extractors/`)

```
ai_chatbot/idp/extractors/
├── __init__.py
├── base.py              # Unified extraction factory — dispatches by MIME type
├── pdf_extractor.py     # pypdf text extraction (falls back to base64 for scanned PDFs)
├── excel_extractor.py   # openpyxl (XLSX) + csv (CSV) tabular extraction
└── docx_extractor.py    # python-docx paragraph + table extraction
```

**base.py — `extract_content(file_url)`:**
- Reads file from Frappe File DocType
- Detects MIME type and dispatches to the appropriate extractor
- Returns unified format: `{content_type: "text"|"image", text/base64, mime_type, file_name}`
- Scanned PDFs (no selectable text) automatically fall back to base64 image for Vision API

### 7.4 ERPNext Schema Discovery (`ai_chatbot/idp/schema.py`)

```python
get_doctype_schema(doctype)   # → {doctype, fields: [...], child_tables: {...}}
build_schema_prompt(doctype)  # → human-readable schema description for LLM
```

- Uses `frappe.get_meta(doctype)` for dynamic field discovery
- Discovers child tables (e.g., Sales Invoice Item) and their field schemas
- Filters to extractable field types (Data, Link, Date, Currency, Float, Int, Select, Table, etc.)
- Identifies Link field targets for fuzzy resolution
- Generates structured text description for the LLM extraction prompt

### 7.5 LLM Semantic Mapper (`ai_chatbot/idp/mapper.py`)

The core of the IDP system. The LLM does all semantic reasoning.

**`extract_and_map(file_url, target_doctype, company)`:**

1. Extract raw content from the file (text or base64 image)
2. Build target DocType schema description via `build_schema_prompt()`
3. Construct structured extraction prompt with:
   - The raw document content (embedded text or Vision API image)
   - The target ERPNext schema (fields, types, constraints, Link targets)
   - Normalization rules (dates → YYYY-MM-DD, numbers → clean floats)
   - Multi-language handling ("identify fields by semantic meaning, not header text")
   - Required JSON output format with `header`, `items`, and `unmapped_fields`
4. Send to configured AI provider via `get_ai_provider().chat_completion()`
5. Parse JSON response (handles markdown fences, explanatory text)
6. Normalize values: date parsing (12+ formats), number cleaning, type coercion

**Extraction prompt strategy:**
- System prompt: "You are an expert data extraction specialist for ERPNext ERP systems"
- User prompt includes full schema with field labels, types, and constraints
- Explicit rules for multi-language support, date normalization, number stripping
- Instruction to return `null` for unidentifiable fields (never guess)
- `unmapped_fields` array for source fields that couldn't be mapped

### 7.6 Post-Extraction Validators (`ai_chatbot/idp/validators.py`)

**`validate_extraction(extracted_data, target_doctype, company)`:**

Three levels of validation:

1. **Schema validation** — required fields present, correct types
2. **Link field resolution** — fuzzy matching of customer/supplier/item names:
   - Exact match on `name` → direct resolve
   - Exact match on display field (customer_name, supplier_name, item_name) → resolve
   - LIKE match on display field → resolve if unique
   - Company-scoped searches for DocTypes with company fields
   - Known display-name fields for 10+ DocTypes (Customer, Supplier, Item, Employee, etc.)
3. **Business rules** — posting_date ≤ due_date, qty > 0, rate ≥ 0, items present for transaction docs

### 7.7 Document Comparison (`ai_chatbot/idp/comparison.py`)

**`compare_with_record(extracted_data, doctype, docname)`:**

- Field-by-field comparison with type-aware matching:
  - Dates: compare via `getdate()` (handles format differences)
  - Currency/Float: compare with `flt(val, 2)` precision
  - Strings: case-insensitive, whitespace-trimmed
- Item-level comparison:
  - Match by `item_code` (preferred) or by position (fallback)
  - Per-row field comparison with individual diff reporting
  - Reports extra items in document and extra items in record
- Output: matches, discrepancies, missing_in_document, missing_in_record, items_comparison, summary

### 7.8 IDP Tools (`ai_chatbot/tools/idp.py`)

Three tools registered with `@register_tool` in the `idp` category:

**Tool 1: `extract_document_data`**
- Extracts structured data from uploaded file and maps to ERPNext schema
- Runs full pipeline: content extraction → LLM mapping → validation → link resolution
- Returns extracted data for user review (never creates a record directly)
- Supported DocTypes: Sales Invoice, Purchase Invoice, Quotation, Sales Order, Purchase Order, Delivery Note, Purchase Receipt

**Tool 2: `create_from_extracted_data`**
- Creates ERPNext record from previously extracted data
- Requires user confirmation (two-step pattern from Phase 3)
- Re-validates before creation
- Uses existing `create_document()` from `data/operations.py`
- Requires both `enable_idp_tools` AND `enable_write_operations`

**Tool 3: `compare_document_with_record`**
- Extracts data from uploaded document, then compares with existing ERPNext record
- Returns field-by-field discrepancy report with match/mismatch indicators
- Use case: vendor invoice vs Purchase Order, client PO vs Sales Order

### 7.9 Settings & Integration

**Chatbot Settings:**
- New field: `enable_idp_tools` (Check) — in Tools tab, default: 0
- New section: "Document Processing (IDP)" between ERPNext Tools and Data Operations

**System Prompt** (`core/prompts.py`):
- New section added when IDP tools are enabled
- Describes the extract → review → confirm → create workflow
- Lists supported document formats and multi-language capability

**Tool Registry** (`tools/registry.py`):
- `import ai_chatbot.tools.idp` added in `_ensure_tools_loaded()`
- IDP tools loaded alongside ERPNext tools (conditional on ERPNext installation)

**Constants** (`core/constants.py`):
- `"idp": "enable_idp_tools"` added to `TOOL_CATEGORIES`

### 7.10 Deliverables

| Item | Files | Status |
|------|-------|--------|
| Content extractors | `idp/extractors/base.py`, `pdf_extractor.py`, `excel_extractor.py`, `docx_extractor.py` | ✅ |
| Schema discovery | `idp/schema.py` | ✅ |
| LLM semantic mapper | `idp/mapper.py` | ✅ |
| Post-extraction validators | `idp/validators.py` | ✅ |
| Document comparison | `idp/comparison.py` | ✅ |
| IDP tools | `tools/idp.py` (3 tools: extract, create, compare) | ✅ |
| Settings integration | Updated `chatbot_settings.json`, `constants.py`, `prompts.py`, `registry.py` | ✅ |

**New dependencies (optional extras):**
- `pypdf>=4.0` — PDF text extraction
- `openpyxl>=3.1` — Excel parsing
- `python-docx>=1.1` — DOCX text extraction
- Install via: `pip install ai_chatbot[idp]`

### 7.11 Post-Release Bug Fixes

#### 7.11.1 Pre-Extraction User Preferences (prompts.py)

The IDP workflow prompt was restructured so the LLM asks for **all missing preferences** before calling `extract_document_data`:

- **Output Language** (default: English) — document can be in any language; extracted values are translated
- **Is Stock Item?** (yes/no)
- **Is Fixed Asset?** (yes/no)
- **Item Group** — ERPNext Item Group name

Each preference is a separate mandatory block with explicit skip-conditions. If the user provides some preferences in their message (e.g., "stock items, Item Group: Consumable"), the LLM asks only for the missing ones (e.g., Output Language, Is Fixed Asset).

**Files changed:** `core/prompts.py`

#### 7.11.2 Output Language Translation (mapper.py, tools/idp.py)

Added `output_language` parameter through the entire extraction pipeline:

- `extract_document_data` tool accepts `output_language` (default: `"English"`)
- Passed through `extract_and_map()` → `_build_extraction_messages()` → `_build_system_prompt()`
- System prompt instructs the LLM to translate text values (item descriptions, terms, remarks, party names) to the target language while preserving numbers, dates, currency codes, and proper nouns

**Files changed:** `tools/idp.py`, `idp/mapper.py`

#### 7.11.3 Item Description Extraction (mapper.py)

Strengthened extraction rules for item fields:

- `description` must be COMPLETE, VERBATIM, UNTRUNCATED — at least as long as `item_name`
- `item_name`: short product name (max ~140 characters)
- `item_code`: product/part code or first 100 chars of description
- Single-column invoices: full text → `description`, first 100 chars → `item_code`/`item_name`

**Files changed:** `idp/mapper.py`

#### 7.11.4 Terms & Remarks Saving (mapper.py, data/operations.py)

Fixed three issues preventing terms and remarks from being saved:

1. **Prompt clarification:** Explicit "use `terms` NOT `tc_name`" and "use `remarks` NOT `bank_details`" instructions with a "Fields to EXCLUDE" section
2. **Field alias normalization:** Added `_FIELD_ALIASES` dict (`terms_and_conditions` → `terms`, `bank_details` → `remarks`, `contact_person` → `contact_display`) applied post-extraction. Detects when `tc_name` contains free text (>50 chars) and moves it to `terms`
3. **Post-insert preservation:** Added `_preserve_text_fields()` helper in `operations.py` that re-applies `terms` and `remarks` after `doc.insert()` if ERPNext hooks cleared them

**Files changed:** `idp/mapper.py`, `data/operations.py`

#### 7.11.5 Auto-Create Missing Masters (tools/idp.py)

Added `create_missing_masters` and `item_defaults_json` parameters to `create_from_extracted_data` tool:

- When missing Items/Customer/Supplier are detected, the LLM asks the user for confirmation and item properties (Is Stock Item?, Is Fixed Asset?, Item Group?)
- `_auto_create_missing_masters()` creates minimal records with user-specified defaults
- `_find_missing_masters()` checks by both `name` and display name fields
- UOM auto-creation included

**Files changed:** `tools/idp.py`

#### 7.11.6 Image Attachments Missing file_url for LLM (api/files.py)

**Bug:** When an image was uploaded (especially with spaces in filename), the LLM could see the image visually (via base64 Vision API) but never received the `file_url`. When calling `extract_document_data`, the LLM guessed wrong file paths (e.g., `/private/files/image.jpg`).

**Root cause:** `build_vision_content()` embedded images as base64 for the Vision API but did not include the `file_url` as a text part. Non-image files already had this (line 467-473 in `streaming.py`), but images did not.

**Fix:** After adding the base64 image content part, now also appends a text part: `[Image file_url: /private/files/..., file_name: ...]` so the LLM knows the exact file path.

**Files changed:** `api/files.py`

#### 7.11.7 Robust File Lookup for URL Encoding (idp/extractors/base.py, api/files.py)

**Bug:** File lookups via `frappe.get_doc("File", {"file_url": file_url})` could fail when the URL had encoding mismatches (spaces vs `%20`).

**Fix:** Added `_get_file_doc()` helper in `base.py` that tries multiple URL variants:
1. Original URL as passed
2. URL-decoded variant (converts `%20` → spaces)
3. URL-re-encoded variant (converts spaces → `%20`, filename portion only)
4. Filename-only fallback (`file_name` field match)
5. Strips domain prefix if LLM passes a full URL

`get_file_base64()` in `api/files.py` also updated to use `_get_file_doc()`.

**Files changed:** `idp/extractors/base.py`, `api/files.py`

#### 7.11.8 Claude API Billing Error Detection (utils/ai_providers.py)

**Bug:** Anthropic returns HTTP 400 (not 429) for billing/credit issues. The error classifier only checked 429 for quota errors.

**Fix:** `classify_api_error()` now checks the response body for billing-related keywords (`credit balance`, `billing`, `purchase credits`) on 400 responses and returns a user-friendly quota exceeded message.

**Files changed:** `utils/ai_providers.py`

---

## Phase 8: Agentic RAG — Vector Search + Multi-Agent Orchestration

**Goal:** Implement vector-based document retrieval with multi-agent orchestration, planning, and iterative refinement. Builds on Phase 7's document extraction by adding persistent knowledge indexing and intelligent query routing.

> **Note:** Per the architectural review (see Q&A section below), this phase may be simplified to focus on multi-agent orchestration (planner + analyst agents) without the RAG/vector store components, unless a clear document search use case emerges.

### 8.1 RAG Foundation (`ai_chatbot/ai/rag/`)

```
ai_chatbot/ai/rag/
├── __init__.py
├── embeddings.py      # Embedding generation (OpenAI/local)
├── vector_store.py    # ChromaDB interface
├── chunker.py         # Document chunking strategies
└── retriever.py       # Query → retrieve → rank → return
```

### 8.2 Agent Framework (`ai_chatbot/ai/agents/`)

```
ai_chatbot/ai/agents/
├── __init__.py
├── base_agent.py          # Abstract agent interface
├── orchestrator.py        # Routes queries to appropriate agent(s)
├── planner_agent.py       # Decomposes complex queries into steps
├── analyst_agent.py       # Data analysis with tool calling
└── document_agent.py      # Document retrieval and synthesis
```

### 8.3 Memory System (`ai_chatbot/ai/memory/`)

```
ai_chatbot/ai/memory/
├── __init__.py
├── conversation_memory.py    # Short-term: current conversation context
├── knowledge_memory.py       # Long-term: persistent knowledge from RAG
└── memory_manager.py         # Manages context window allocation
```

### 8.4 Knowledge Base DocType & Indexing

**Chatbot Knowledge Base** (new DocType):
- Fields: `title`, `source_type` (File/ERPNext Record/URL), `source_reference`, `company`, `status` (Indexed/Pending/Failed), `chunk_count`, `last_indexed`
- Tracks what has been indexed into the vector store

### 8.5 Deliverables

| Item | Files |
|------|-------|
| RAG engine | `ai/rag/embeddings.py`, `vector_store.py`, `chunker.py`, `retriever.py` |
| Agent framework | `ai/agents/base_agent.py`, `orchestrator.py`, `planner_agent.py`, `analyst_agent.py`, `document_agent.py` |
| Memory system | `ai/memory/conversation_memory.py`, `knowledge_memory.py`, `memory_manager.py` |
| Knowledge Base DocType | `chatbot/doctype/chatbot_knowledge_base/` |
| Frontend | `KnowledgeBaseView.vue`, `DocumentUploader.vue`, `DocumentList.vue`, `AgentThinking.vue` |

**New dependencies:**
- **Backend:** `chromadb`, `openai` (for embeddings)
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

**Approach:** Start with statistical models (moving averages, exponential smoothing) before adding ML. This avoids heavy dependencies initially.

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
- `detect_anomalies(company, from_date, to_date)` — flags unusual transactions (large amounts, unusual frequency, new suppliers with large orders)
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
- **Enhanced:** `prophet` (Facebook's time series forecasting — optional, heavier install)
- **Advanced (future):** `scikit-learn`, `xgboost` — only when needed

---

## Phase 10: Automation — Scheduled Reports via Email ✅ Done

**Goal:** AI-generated scheduled reports delivered via email on configurable schedules.

### 10.1 Auto Email & Scheduled Reports

**Files:**
- `ai_chatbot/automation/scheduled_reports.py` — scheduler entry point, schedule evaluation, report execution
- `ai_chatbot/automation/executor.py` — headless AI execution engine (multi-round tool loop)
- `ai_chatbot/automation/formatters.py` — HTML email/PDF formatting, markdown preprocessing, ECharts SSR (SVG for PDF, HTML table for email)
- `ai_chatbot/automation/echart_ssr.cjs` — Node.js ECharts server-side SVG renderer (no browser required)
- `ai_chatbot/automation/notifications/dispatcher.py` — email dispatch routing
- `ai_chatbot/automation/notifications/channels/email.py` — email sending via `frappe.sendmail()`
- `ai_chatbot/core/ai_utils.py` — shared AI response parsing (extracted from `chat.py`)

**Chatbot Scheduled Report** DocType (`autoname: format:CSR-{#####}`):
- **Report Configuration tab:**
  - `report_name` (Data, required) — user-defined name
  - `prompt` (Text, required) — the prompt to execute
  - `company` (Link: Company, required) — company context for the report
  - `format` (Select) — Email HTML / PDF / Both (default: Email HTML)
  - `enabled` (Check, default: 1) — active/inactive toggle
- **Schedule tab:**
  - `schedule` (Select, required) — Daily / Weekly / Monthly / Custom Cron
  - `time_of_day` (Time, default: 08:00) — server timezone
  - `day_of_week` (Select, depends_on: Weekly) — Monday–Sunday
  - `day_of_month` (Int, depends_on: Monthly) — 1–28
  - `cron_expression` (Data, depends_on: Custom Cron) — standard cron format
- **Recipients tab:**
  - `recipients` (Table: Chatbot Report Recipient, required) — email recipients
  - `sender` (Link: Email Account) — optional sender override; defaults to system outgoing account
- **Execution Status section (read-only):**
  - `last_run`, `last_run_status` (Success/Failed), `run_count`, `last_error`

**Chatbot Report Recipient** child table DocType:
- `recipient_email` (Data, Email, required) — email address
- `user` (Link: User) — optional Frappe user reference

**AI Provider:** Always uses the global AI provider configured in Chatbot Settings (no per-report override).

**Execution flow:**
1. Frappe scheduler runs `run_scheduled_reports()` every 15 minutes via cron
2. Checks `enable_automation` master toggle in Chatbot Settings
3. Queries all enabled reports and evaluates each schedule (Daily/Weekly/Monthly/Custom Cron)
4. Due reports are enqueued as background jobs (`frappe.enqueue`, queue="long", timeout=600)
5. Each job runs `execute_prompt()` — headless AI with multi-round tool calling as Administrator
6. Response is formatted as styled HTML — separate versions for email and PDF
7. For PDF: charts rendered as inline SVG via ECharts SSR (Node.js, `echart_ssr.cjs`)
8. For email: charts rendered as styled HTML tables (Gmail strips SVG and corrupts base64 data URIs)
9. Email is dispatched via `frappe.sendmail()` with optional sender (Email Account) override
10. Report status is updated (last_run, last_run_status, run_count, last_error)

**Chart rendering strategy:**
- **PDF:** ECharts option → Node.js SSR → inline SVG (works in wkhtmltopdf and Chrome)
- **Email:** ECharts option → styled HTML table with inline CSS (universal email client support)
- `echart_ssr.cjs` uses ECharts 6.0 SSR mode (`renderer: 'svg', ssr: true`) — no browser/DOM required
- `_svg_to_png_img()` via ImageMagick is available but unused (Gmail corrupts large base64 data URIs)
- Supports all chart types: bar, line, pie, horizontal bar, multi-series, stacked bar

**Markdown preprocessing:**
- AI models sometimes write inline bullet lists (`text * item1 * item2`) which `markdown2` doesn't parse as lists
- `_fix_markdown_lists()` preprocessor reformats inline `*` items with proper newlines before HTML conversion
- Ensures consistent rendering between chatbot frontend (`marked.js`) and email/PDF (`markdown2`)

### 10.2 Shared AI Utilities

**`ai_chatbot/core/ai_utils.py`** — extracted from `chat.py` for reuse by the automation executor:
- `is_openai_format(provider_name)` — returns True for OpenAI/Gemini format
- `extract_response(provider_name, response)` — extracts content, tool_calls, token counts
- `extract_tool_info(provider_name, tool_call)` — extracts func_name and func_args

Both `chat.py` and `executor.py` import from this shared module.

### 10.3 Settings

**Chatbot Settings** — Automation tab:
- `enable_automation` (Check, default: 0) — master toggle for all scheduled report execution

### 10.4 Scheduler Configuration

**`hooks.py`:**
```python
scheduler_events = {
    "cron": {
        "*/15 * * * *": [
            "ai_chatbot.automation.scheduled_reports.run_scheduled_reports",
        ],
    },
}
```

### 10.5 Deliverables

| Item | Files |
|------|-------|
| Scheduled reports | `automation/scheduled_reports.py`, `Chatbot Scheduled Report` DocType |
| Headless executor | `automation/executor.py` |
| HTML formatters | `automation/formatters.py` (markdown fix, dual email/PDF rendering) |
| ECharts SSR | `automation/echart_ssr.cjs` (Node.js SVG renderer for PDF charts) |
| Email channel | `automation/notifications/channels/email.py` |
| Dispatcher | `automation/notifications/dispatcher.py` |
| Shared AI utils | `core/ai_utils.py` |
| Hooks | Updated `hooks.py` with scheduler_events (cron every 15 min) |
| Settings | `enable_automation` toggle in Chatbot Settings Automation tab |
| Run Now button | `chatbot_scheduled_report.js` (manual trigger from form UI) |

**New dependencies:** None. Uses only existing Frappe email infrastructure.

---

## Phase 11: PDF Export from Chat ✅ Done

**Goal:** Allow users to export any AI chatbot response (including tables and charts) as a downloadable PDF directly from the chat interface. Both single-message and full-conversation exports are supported.

### 11.1 Backend — PDF Generation API

**New file:** `ai_chatbot/api/export.py`

Two whitelisted endpoints:

```python
@frappe.whitelist()
def export_message_pdf(message_name: str) -> dict:
    """Generate a PDF from a single Chatbot Message and return the file URL."""

@frappe.whitelist()
def export_conversation_pdf(conversation_id: str) -> dict:
    """Generate a PDF containing all messages in a conversation."""
```

**Pipeline (per message):**
1. `_fix_markdown_structure()` — ensures blank lines before lists and heading markers on their own line
2. `_fix_markdown_lists()` — converts inline dash-lists (`text - a - b - c`) to proper markdown lists
3. `_markdown_to_html()` — `markdown2` conversion (via `frappe.utils.md_to_html`)
4. `_replace_hr_tags()` — replaces `<hr>` with a lightweight `<p>` separator (mitigates wkhtmltopdf centering bug)
5. `_style_html_tables()` — adds borders, padding, 11px font via `_merge_or_add_style()` (merges with existing `style=` attributes from markdown2's column alignment)
6. `_style_html_headings()` — replaces `<h1>`–`<h6>` with styled `<p>` tags (bypasses wkhtmltopdf heading centering bug)
7. `_render_charts()` — ECharts → inline SVG for PDF, HTML table fallback for email (with notice)

**Key design decisions:**
- Reuses `automation/formatters.py` rendering pipeline — identical output for download PDF, email PDF, and scheduled reports
- `_merge_or_add_style()` helper merges our border/padding styles with markdown2's existing `text-align:right` on column-aligned tables (`:---:` syntax)
- Heading `<h1>`–`<h6>` tags are replaced with styled `<p>` tags because wkhtmltopdf centers headings near page breaks regardless of CSS
- `_PDF_STYLE_BLOCK` provides CSS `!important` overrides for body/heading/table alignment
- Permission check: only the owning user can export their own messages/conversations
- Files saved as private Frappe File attachments with sanitised filenames (max 30 chars + message/conversation name + date)

### 11.2 Frontend — Download Button

**Updated files:** `frontend/src/components/ChatMessage.vue`, `frontend/src/pages/ChatView.vue`, `frontend/src/utils/api.js`

- "Download PDF" icon button on assistant messages (next to copy button)
- On click → calls `export_message_pdf` → receives file URL → triggers browser download
- Loading spinner while PDF generates
- `ChatAPI` class extended with `exportMessagePDF()` and `exportConversationPDF()` methods

### 11.3 Markdown Preprocessing Functions (in `automation/formatters.py`)

| Function | Purpose |
|----------|---------|
| `_fix_markdown_structure()` | Inserts blank lines before dash/asterisk-lists (required by `markdown2`) and splits inline heading markers onto their own line |
| `_fix_markdown_lists()` | Converts inline dash-lists (`text - a - b - c`) to proper markdown bullet lists |
| `_replace_hr_tags()` | Replaces `<hr>` with minimal `<p>` separator to mitigate wkhtmltopdf page-break alignment bug |
| `_merge_or_add_style()` | Merges CSS into existing `style=` attributes or adds new ones — handles markdown2's column-alignment styles |
| `_style_html_tables()` | Adds borders, padding, font-size to `<table>`, `<th>`, `<td>` using `_merge_or_add_style()` |
| `_style_html_headings()` | Replaces `<h1>`–`<h6>` with styled `<p>` tags (size, weight, color, `page-break-inside: avoid`) |

### 11.4 Deliverables

| Item | Files |
|------|-------|
| PDF export API | `api/export.py` (`export_message_pdf`, `export_conversation_pdf`) |
| Markdown/HTML formatters | `automation/formatters.py` (shared pipeline for email + PDF) |
| Frontend button + API | `ChatMessage.vue`, `ChatView.vue`, `api.js` |

**New dependencies:** None (uses existing `frappe.utils.pdf` / wkhtmltopdf).

### 11.5 Known Limitations

- **wkhtmltopdf page-break centering:** A small number of headings (typically 2–3 per long document) may appear centered when they land exactly at a wkhtmltopdf page break boundary after a separator element. This is a known wkhtmltopdf engine bug that affects even `<p>` tags with explicit `text-align: left !important`. The recommended future fix is migrating to **weasyprint** which has correct CSS page-break handling.
- **Charts in email:** ECharts are rendered as HTML tables in email (SVG not supported by most email clients). A notice is included informing recipients of the substitution.

---

## Phase Summary

| Phase | Focus | Priority | Status | Key Deliverable | Dependencies Added |
|-------|-------|----------|--------|------------------|--------------------|
| **1** | Foundation | — | ✅ Done | Data layer, multi-company/currency, security fixes | None |
| **2** | Streaming | — | ✅ Done | Frappe Realtime token streaming, enhanced chat UX | None |
| **3** | CRUD | — | ✅ Done | Create/update/delete ERPNext records via chat | None |
| **4** | Finance | — | ✅ Done | 17 finance tools, ECharts integration, multi-color charts | echarts (npm) |
| **5** | HRMS & CRM | — | ✅ Done | 6 HRMS tools, 5 CRM tools with charts | None |
| **5A** | UX & Accessibility | — | ✅ Done | File upload + Vision API, voice I/O, @mentions, sidebar toggle | None |
| **5B** | Enterprise Analytics | — | ✅ Done | Permissions, dimensions, CFO dashboard, consolidation, config, plugins | None |
| **6** | Settings & Gemini | High | ✅ Done | Unified provider config, Gemini, token/cost tracking, file headers | None |
| **6A** | UI Overhaul | High | ✅ Done | Claude-style sidebar, process indicators, greeting, search, dark mode | None |
| **6B** | Multi-Dim Analytics | Medium | ✅ Done | Hierarchical grouping, GL Entry finance, BI cards, sidebar/greeting refinements | None |
| **6C** | Workspace & Help | Low | ✅ Done | Frappe workspace, help button, language selector | None |
| **7** | IDP | Medium | ✅ Done | Document extraction, schema mapping, comparison/reconciliation | pypdf, openpyxl, python-docx (opt) |
| **8** | Multi-Agent | Medium | ✅ Done | Multi-agent orchestration for complex queries | None |
| **9** | Predictive | Low | ✅ Done | Forecasting, anomaly detection | None (statistical methods) |
| **10** | Automation | Low | ✅ Done | Scheduled reports via email, headless AI executor | None |
| **11** | PDF Export | Low | ✅ Done | Single-message & conversation PDF export, robust markdown/HTML pipeline | None |

---

## Multi-Company & Multi-Currency Reference

### Multi-Company Pattern

Every tool that queries transactional data follows this pattern:

```python
def get_sales_analytics(from_date=None, to_date=None, company=None):
    """Get sales analytics for a specific company."""
    company = get_default_company(company)  # Resolves: passed → user default → global default

    filters = {"docstatus": 1, "company": company}
    ...

    return build_currency_response(result, company)
    # Adds: {"company": company, "currency": "USD"}
```

### Multi-Currency Pattern

For monetary aggregations, always use base currency fields:

| DocType | Transaction Amount | Base Amount (use this) |
|---------|-------------------|----------------------|
| Sales Invoice | `grand_total` | `base_grand_total` |
| Purchase Invoice | `grand_total` | `base_grand_total` |
| Sales Order | `grand_total` | `base_grand_total` |
| Purchase Order | `grand_total` | `base_grand_total` |
| Payment Entry | `paid_amount` | `base_paid_amount` |
| Opportunity | `opportunity_amount` | (convert manually using party currency) |
| Journal Entry | `debit` / `credit` | `debit_in_account_currency` is the foreign; `debit` is base |

### Parent Company Consolidation (Phase 5B)

When a company is a parent company:
1. Detect child companies via `frappe.db.get_descendants("Company", parent_company)`
2. Ask user: include subsidiaries? In which currency?
3. Execute tool across all companies
4. Convert to target currency using `get_exchange_rate()`
5. Aggregate and present consolidated view

### Company Isolation for RAG (Phase 8)

Vector store collections are namespaced by company:
- Collection name: `knowledge_{company_name_slug}`
- Queries only search the current user's company collection
- Cross-company search requires explicit permission

---

## Architectural Queries & Recommendations

### Q: pandas, numpy for data analysis — will it make a difference?

**Recommendation: Not needed now. Consider for Phase 9 (Predictive) only.**

For the current tool-based analytics (Phases 1–6B), `frappe.qb` (Query Builder) handles all aggregation, grouping, and filtering at the database level — which is more efficient than pulling raw data into Python for processing. pandas/numpy would add ~200MB to the install footprint and introduce memory concerns for large datasets.

**When they become useful:**
- **Phase 9 (Predictive Analytics):** Time series decomposition, moving averages, trend analysis — pandas is the right tool here
- **Phase 6B (Multi-Dimensional Grouping):** If pivot-table-like operations become complex, pandas `pivot_table()` could simplify the code — but SQL GROUP BY with ROLLUP can handle most cases

**Recommendation per library:**
| Library | Verdict | When |
|---------|---------|------|
| `pandas` | Use in Phase 9 | Time series, forecasting, pivot tables |
| `numpy` | Use with pandas | Comes as pandas dependency |
| `matplotlib/seaborn` | Skip | ECharts handles all visualization (client-side) |
| `pydantic` | Skip | Frappe's DocType validation is sufficient; tools use simple dicts |
| `scipy/sklearn` | Phase 9+ only | Only if ML-based anomaly detection or forecasting is needed |

### Q: How to show tools added by other applications?

**Already implemented (Phase 5B.8).** External apps register tools via the `ai_chatbot_tool_modules` Frappe hook in their `hooks.py`. The registry dynamically loads and exposes these tools. See Phase 5B.8 in this roadmap for details.

### Q: Desk Page — can we create ai-chatbot as a Frappe desk page?

**Current approach is correct and better.** The app already uses Frappe's portal page pattern (`www/ai-chatbot.html` + `www/ai_chatbot.py`), which is the same pattern used by Frappe CRM. This gives full control over the layout (no Frappe desk chrome/sidebar interfering with the chat UI).

**For desk integration:** Phase 6C adds a Frappe Workspace with a shortcut link to `/ai-chatbot`. This gives users a desk-accessible entry point while keeping the full-screen chat experience. The workspace also shows admin shortcuts (Settings, Conversations, Token Usage).

### Q: Smart Compose & Autocomplete — predictive text suggestions?

**Feasible but not recommended for current scope.** This would require:
- Client-side text prediction model (large JS bundle) or server-round-trip per keystroke (latency)
- The @mention system (Phase 5A) already provides structured autocomplete for common parameters
- Low ROI: users type free-form natural language — predicting the next word in "Show me sales for..." is less useful than in structured search

**If desired later:** Could be implemented as a lightweight Phase 11 using the browser's built-in `<datalist>` element with a curated list of common prompt fragments.

### Q: Artifact Streaming — what is it?

**Artifact streaming** (as implemented by Claude.ai and similar) is a pattern where the AI generates a distinct, self-contained artifact (code file, document, diagram) separately from the conversational response. The artifact streams into a dedicated side panel while the conversation continues in the main panel.

**How it differs from normal streaming:**
- Normal streaming: tokens flow sequentially into one output area
- Artifact streaming: the AI signals "I'm creating an artifact" and tokens route to a separate panel

**Relevance to this project:** Low. The chatbot's outputs are conversational responses with inline charts/tables — not standalone artifacts. The ECharts rendering already handles the "rich output" use case. Artifact streaming would add complexity without clear benefit for ERP analytics. Skip.

### Q: Chatbot Audit Log — is it needed?

**Partially implemented, sufficient for now.** The current system already tracks:
- All messages (Chatbot Message DocType) with timestamps, user, tokens used
- Tool calls and results (stored as JSON in message records)
- Conversation metadata (total tokens, message count)

**Phase 6 adds:** Per-request token usage tracking with cost estimates (Chatbot Token Usage DocType).

**What's not tracked (and probably not needed):**
- Prompt injection attempts — the AI is read-only by default (write ops require explicit enable)
- Detailed latency metrics — can be added later as a Phase 2.2 tool performance monitor (see todo_II item 2.2)
- A separate "audit log" DocType would be redundant with the existing message/token tracking

### Q: Agentic RAG + Memory — is it necessary given the limited scope?

**Re-evaluation based on your clarified scope** (no document search, only extract structured data from documents for creating ERPNext records or comparing with existing records):

**Agentic RAG is NOT needed.** Your use case is **Intelligent Document Processing (IDP)**, which is already planned as Phase 8. The IDP approach (LLM Vision → structured extraction → ERPNext mapping) does not require vector stores, embeddings, or retrieval.

**Memory system is partially useful:**
- **Conversation memory** — already implemented (messages stored in DB, context window managed)
- **Knowledge memory** (long-term) — not needed without document search
- **Memory manager** (context allocation) — addressed by Phase 6.4 token optimization

**Recommendation:** Simplify Phase 8 (Agentic RAG) to focus only on the multi-agent orchestration pattern (planner + analyst agents) for complex multi-step queries. Drop the RAG/vector store components unless a clear document search use case emerges. Phase 7 (IDP) now handles the document extraction and record creation use case.

### Q: Python Libraries recommendation

| Library | Recommendation | Rationale |
|---------|---------------|-----------|
| `pandas` | Phase 9 only | Overkill for SQL-based aggregations; valuable for time series and forecasting |
| `numpy` | Phase 9 only | Comes with pandas; needed for statistical operations |
| `matplotlib/seaborn` | Skip entirely | All visualization is ECharts (client-side); no server-side chart rendering needed |
| `pydantic` | Skip | Frappe DocTypes + simple dicts are sufficient; adding pydantic would be a parallel validation layer |
| `scipy` | Phase 9 only | Statistical tests, anomaly detection (z-score, IQR) |
| `sklearn` | Phase 9+ only | Only if ML-based forecasting or classification is needed |

**Memory considerations:** ERPNext datasets are moderate (thousands to low millions of records). SQL aggregations with proper indexes handle this efficiently. Pulling large datasets into pandas DataFrames would increase memory usage — keep processing at the DB level via `frappe.qb`.

### Q: Tool Performance Monitoring

**Planned as part of Phase 6.5 (Cost Monitoring).** The token tracker records per-request metrics. Adding LLM latency and prompt-to-response timing is a natural extension:
- Record `start_time` and `end_time` for each AI call
- Record tool execution time per tool call
- Expose via a `get_performance_metrics` tool so admins can ask "Which tools are slowest?"

---

## Future-Proofing Architecture

The current architecture already supports several future-proofing patterns:

| Pattern | Status | Implementation |
|---------|--------|----------------|
| **Modular AI provider abstraction** | ✅ Done | `AIProvider` base class in `ai_providers.py` — add new providers by subclassing |
| **Pluggable tool framework** | ✅ Done | `@register_tool` decorator + hooks-based plugin loading (Phase 5B.8) |
| **LLM-agnostic architecture** | ✅ Done | Unified provider config; all providers use the same tool schema format |
| **Event-driven processing** | ✅ Done | Streaming via `frappe.publish_realtime` (Redis Pub/Sub + Socket.IO) |
| **Agentic orchestration readiness** | Phase 8 | Multi-agent framework with planner + analyst agents |
| **Graph-based execution** | Phase 8+ | Could be added to the planner agent for complex query decomposition |

---

## File Structure After All Phases

```
ai_chatbot/
├── core/                          # Phase 1
│   ├── ai_utils.py                # Phase 10 (shared AI response parsing for chat + automation)
│   ├── config.py                  # Updated: Phase 5B (configurable constants)
│   ├── constants.py               # Updated: Phase 5B (dynamic categories), 10 (AUTOMATION_MAX_TOOL_ROUNDS)
│   ├── exceptions.py
│   ├── logger.py
│   ├── prompts.py                 # Updated: Phase 5B (configurable prompts), 10 (optional company param)
│   ├── dimensions.py              # Phase 5B (accounting dimension helpers)
│   └── consolidation.py           # Phase 5B (parent company consolidation)
│
├── data/                          # Phase 1, 3, 4
│   ├── queries.py
│   ├── analytics.py
│   ├── currency.py
│   ├── charts.py                  # Phase 4, 6B (ECharts builders + stacked bar)
│   ├── grouping.py                # Phase 6B (multi-dimensional grouping engine)
│   ├── operations.py              # Phase 3
│   └── validators.py              # Phase 3
│
├── api/                           # Phase 1, 2, 3, 5A, 11
│   ├── chat.py                    # Updated: 5A (attachments, @mention endpoint)
│   ├── export.py                  # Phase 11 (PDF export: single message + full conversation)
│   ├── streaming.py               # Phase 2, updated: 5A (attachments, vision content)
│   └── files.py                   # Phase 5A (file upload, vision content builder)
│
├── utils/
│   └── ai_providers.py            # Updated: 5A (Claude multimodal/vision content conversion)
│
├── tools/                         # Phase 1, 3, 4, 5, 5B, 7
│   ├── registry.py                # Phase 1, updated: 5B (permissions, plugins), 7 (IDP import)
│   ├── base.py
│   ├── crm.py                     # Phase 1, updated: 5
│   ├── selling.py                 # Phase 1, updated: 4
│   ├── buying.py                  # Phase 1, updated: 4
│   ├── stock.py                   # Phase 1, updated: 4
│   ├── account.py                 # Phase 1
│   ├── hrms.py                    # Phase 5
│   ├── idp.py                     # Phase 7 (IDP: extract, create, compare tools)
│   ├── reports.py                 # Phase 5B (report data tools)
│   ├── operations/                # Phase 3
│   │   ├── create.py
│   │   ├── update.py
│   │   └── search.py
│   ├── finance/                   # Phase 4, 5B
│   │   ├── budget.py
│   │   ├── ratios.py
│   │   ├── profitability.py
│   │   ├── working_capital.py
│   │   ├── receivables.py
│   │   ├── payables.py
│   │   ├── cash_flow.py
│   │   ├── cfo.py                 # Phase 5B, 6B (CFO composite reports + BI cards)
│   │   ├── analytics.py           # Phase 6B (multi-dimensional summary tool)
│   │   └── gl_analytics.py        # Phase 6B (GL Entry-based tools)
│   └── predictive/                # Phase 8
│       ├── demand_forecast.py
│       ├── sales_forecast.py
│       ├── cash_flow_forecast.py
│       └── anomaly_detection.py
│
├── idp/                           # Phase 7 (Intelligent Document Processing)
│   ├── extractors/
│   │   ├── base.py                # Unified extraction factory
│   │   ├── pdf_extractor.py       # pypdf text extraction
│   │   ├── excel_extractor.py     # openpyxl (XLSX) + csv extraction
│   │   └── docx_extractor.py      # python-docx extraction
│   ├── schema.py                  # ERPNext DocType schema discovery
│   ├── mapper.py                  # LLM semantic extraction + schema mapping
│   ├── validators.py              # Post-extraction validation + link resolution
│   └── comparison.py              # Document vs record comparison
│
├── ai/                            # Phase 8 (Agentic RAG — planned)
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── chunker.py
│   │   └── retriever.py
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── orchestrator.py
│   │   ├── planner_agent.py
│   │   ├── analyst_agent.py
│   │   └── document_agent.py
│   └── memory/
│       ├── conversation_memory.py
│       ├── knowledge_memory.py
│       └── memory_manager.py
│
├── automation/                    # Phase 10, 11
│   ├── echart_ssr.cjs             # Node.js ECharts SSR → SVG (for PDF charts)
│   ├── executor.py                # Headless AI execution engine
│   ├── formatters.py              # HTML email/PDF formatting, markdown preprocessing, chart rendering (updated: 11)
│   ├── scheduled_reports.py       # Scheduler entry point, schedule evaluation
│   └── notifications/
│       ├── channels/
│       │   └── email.py           # Email via frappe.sendmail
│       └── dispatcher.py          # Email dispatch routing
│
├── chatbot/                       # Frappe DocTypes (expanded across phases)
│   └── doctype/
│       ├── chatbot_settings/      # Updated: 5A, 5B (prompts, constants), 7 (IDP), 10 (enable_automation)
│       ├── chatbot_conversation/
│       ├── chatbot_message/       # Updated: 4 (tool_results), 5A (attachments)
│       ├── chatbot_knowledge_base/    # Phase 8
│       ├── chatbot_scheduled_report/  # Phase 10 (autoname: CSR-{#####})
│       └── chatbot_report_recipient/  # Phase 10 (child table)
│
└── tests/                         # All phases
    ├── unit/
    ├── integration/
    └── fixtures/

frontend/src/
├── components/
│   ├── Sidebar.vue                # Updated: 5A (collapsible via parent CSS)
│   ├── ChatHeader.vue             # Updated: 5A (sidebar toggle button)
│   ├── ChatMessage.vue            # Updated: 4 (charts), 5A (attachments, speaker button), 11 (PDF download)
│   ├── ChatInput.vue              # Updated: 5A (file upload, voice, @mentions, suggestions)
│   ├── TypingIndicator.vue
│   ├── charts/                    # Phase 4, 5A, 6B
│   │   ├── EChartRenderer.vue
│   │   ├── ChartMessage.vue       # Updated: 5A (multi-chart)
│   │   ├── BiCards.vue            # Phase 6B (BI metric cards)
│   │   ├── HierarchicalTable.vue  # Phase 6B (indented data table)
│   │   └── DataTable.vue          # Phase 5A (styled tables)
│   ├── documents/                 # Phase 8
│   │   ├── DocumentUploader.vue
│   │   └── DocumentList.vue
│   └── chat/
│       └── AgentThinking.vue      # Phase 8
├── pages/
│   ├── ChatView.vue               # Updated: 5A (sidebar toggle, payload handling, voice output, suggestions), 11 (PDF export)
│   └── KnowledgeBaseView.vue      # Phase 8
├── composables/
│   ├── useStreaming.js             # Phase 2
│   ├── useSocket.js               # Phase 2
│   ├── useVoiceInput.js           # Phase 5A (speech-to-text)
│   ├── useVoiceOutput.js          # Phase 5A (text-to-speech)
│   └── useFileUpload.js           # Phase 5A (file selection/validation/preview)
└── utils/
    ├── api.js                     # Updated: 5A (uploadFile, getMentionValues, attachments), 11 (exportMessagePDF, exportConversationPDF)
    └── markdown.js                # Phase 2
```
