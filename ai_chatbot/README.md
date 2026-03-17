# AI Chatbot for ERPNext

An intelligent conversational assistant for ERPNext, built on the Frappe framework. It connects to OpenAI, Anthropic Claude, or Google Gemini and provides 46+ business intelligence tools that query live ERPNext data -- sales, finance, HR, inventory, CRM, and more -- directly from a chat interface.

Version 0.0.1 | License: MIT | Author: Sanjay Kumar

---

## Features

### Chat Interface
- Modern single-page chat UI built with Vue 3, Vite, and Tailwind CSS
- Sidebar with conversation history, provider switcher, and dark mode toggle
- Responsive layout (desktop and mobile)
- Markdown rendering (marked.js) with syntax highlighting (highlight.js)
- PDF export of individual messages or full conversations

### AI Providers
- OpenAI: GPT-4o, GPT-4-Turbo, GPT-3.5-Turbo
- Anthropic Claude: Opus 4.5, Sonnet 4.5, Haiku 4.5
- Google Gemini
- Switch providers on the fly from the sidebar

### Real-Time Streaming
- Token-by-token streaming via Frappe Realtime (Socket.IO / WebSocket)
- Typing indicator while the AI is generating a response

### ERPNext Business Intelligence Tools (46+)

**CRM** -- Lead stats, opportunity pipeline, lead conversion rates, sales funnel, lead source analysis

**Sales / Selling** -- Sales analytics, top customers, sales trend, revenue by territory, revenue by item group

**Buying / Purchase** -- Purchase analytics, supplier performance, purchase trend, purchase by item group

**Finance** -- Financial summary, cash flow, GL analytics, profitability, financial ratios, budget vs actual, receivables aging, payables aging, working capital, CFO dashboard

**Inventory / Stock** -- Stock summary, low stock alerts, stock movement, stock ageing

**HRMS** -- Employee count, attendance summary, leave balance, payroll summary, department-wise salary, employee turnover

**IDP (Intelligent Document Processing)** -- Document extraction via LLM Vision API, ERPNext record creation from extracted data, document comparison

**Predictive Analytics** -- Sales forecast, demand forecast, cash flow forecast, anomaly detection

**Operations (CRUD)** -- Create, search, and update ERPNext records through conversational commands

**Consolidation** -- Cross-company consolidated reports for multi-company setups

**Session** -- Include-subsidiaries toggle, target currency selection

### Multi-Company and Multi-Currency
- Every tool accepts a `company` parameter (defaults to the user's default company)
- Monetary aggregations use `base_*` fields for company-currency consistency
- Cross-company consolidated reports for group-level analysis
- Per-conversation target currency selection

### Additional Capabilities
- @mention system for inline context (see below)
- File upload with LLM Vision API support (images, PDFs)
- Voice input/output (speech-to-text, text-to-speech)
- Token usage tracking and cost estimation per request
- Scheduled reports with email and PDF delivery
- Multi-agent orchestration for complex, multi-step queries
- Context optimization: last 20 messages retained, chart data stripped from history
- Configurable AI persona, system prompt, and response language (10 languages)
- Per-conversation language override
- Tool plugin system for extending with custom tools from external Frappe apps

---

## Prerequisites

- Frappe Framework (v15+)
- ERPNext (v15+) -- required for business intelligence tools
- HRMS app -- optional, required only for HR tools
- Python 3.14+
- Node.js 18+
- An API key from at least one supported provider (OpenAI, Anthropic, or Google)

---

## Installation

```bash
# Get the app
bench get-app https://github.com/sanjay-kumar001/ai_chatbot

# Install on your site
bench --site <your-site> install-app ai_chatbot

# Run migrations
bench --site <your-site> migrate

# Build frontend assets
bench build --app ai_chatbot

# Restart
bench restart
```

For IDP (document processing) features, install optional dependencies:

```bash
pip install pypdf>=4.0 openpyxl>=3.1 python-docx>=1.1
```

Or install via the extras group:

```bash
pip install ai_chatbot[idp]
```

---

## Configuration

1. Navigate to **Chatbot Settings** at `/app/chatbot-settings`
2. Select your AI Provider (OpenAI, Claude, or Gemini)
3. Enter the corresponding API key (stored encrypted via Frappe's Password field)
4. Enable or disable tool categories (CRM, Sales, Purchase, Finance, Inventory, HRMS, Operations, IDP, Predictive)
5. Optionally configure:
   - AI persona and system prompt
   - Default response language
   - Scheduled report settings

---

## Usage

After setup, open the chatbot at:

```
https://<your-site>/ai-chatbot
```

Type natural-language questions about your business data. Examples:

| Prompt | Output Type |
|--------|-------------|
| Show top 10 customers by revenue this year | Table |
| Sales trend month by month for this fiscal year | Chart |
| What are our outstanding receivables? | Table |
| What is the current cash balance? | Number |
| Show expense breakdown by cost center | Chart |
| Create a new Lead for John Doe from Acme Corp | Record creation |
| Compare sales this month vs last month | Table |

Charts are rendered with Apache ECharts. The backend returns `echart_option` objects; the frontend renders them inline in the chat.

See [docs/SAMPLE_USER_PROMPT.md](../docs/SAMPLE_USER_PROMPT.md) for a full list of sample prompts organized by category.

---

## @Mention System

Type `@` in the chat input to insert contextual filters. Mentions are resolved to actual ERPNext values before being sent to the AI.

| Mention | Purpose | Example |
|---------|---------|---------|
| `@company` | Filter by company | `@company:Acme Inc` |
| `@period` | Set date range | `@period:this quarter` |
| `@cost_center` | Filter by cost center | `@cost_center:Main` |
| `@department` | Filter by department | `@department:Sales` |
| `@warehouse` | Filter by warehouse | `@warehouse:Stores - A` |
| `@customer` | Filter by customer | `@customer:John Doe` |
| `@item` | Filter by item | `@item:Widget A` |
| `@accounting_dimension` | Filter by custom dimension | `@accounting_dimension:Project X` |

---

## Architecture Overview

```
ai_chatbot/                          # Python package (Frappe backend)
|
|-- api/
|   |-- chat.py                      # @frappe.whitelist() endpoints
|
|-- chatbot/doctype/
|   |-- chatbot_settings/            # Single DocType: provider config, toggles
|   |-- chatbot_conversation/        # Conversation records with session context
|   |-- chatbot_message/             # Messages with tool calls, attachments
|   |-- chatbot_token_usage/         # Per-request token and cost tracking
|   |-- chatbot_scheduled_report/    # Scheduled report configuration
|
|-- core/
|   |-- config.py                    # App configuration helpers
|   |-- constants.py                 # App-wide constants
|   |-- exceptions.py                # Custom exception classes
|   |-- logger.py                    # Logging utilities
|
|-- tools/
|   |-- registry.py                  # Decorator-based tool registration system
|   |-- base.py                      # Backward-compatible wrapper
|   |-- crm.py                       # CRM tools
|   |-- selling.py                   # Selling tools
|   |-- buying.py                    # Buying tools
|   |-- account.py                   # Accounting tools
|   |-- stock.py                     # Inventory tools
|   |-- hrms.py                      # HRMS tools (loaded if HRMS installed)
|   |-- idp.py                       # Intelligent Document Processing
|   |-- session.py                   # Session context tools
|   |-- consolidation.py             # Cross-company consolidation
|   |-- finance/                     # Finance sub-modules
|   |   |-- analytics.py, budget.py, cash_flow.py, cfo.py,
|   |   |-- gl_analytics.py, payables.py, profitability.py,
|   |   |-- ratios.py, receivables.py, working_capital.py
|   |-- predictive/                  # Predictive analytics sub-modules
|   |   |-- sales_forecast.py, demand_forecast.py,
|   |   |-- cash_flow_forecast.py, anomaly_detection.py
|   |-- operations/                  # CRUD operations
|       |-- create.py, search.py, update.py
|
|-- utils/
|   |-- ai_providers.py              # OpenAI, Claude, Gemini API integration
|
|-- automation/
|   |-- scheduled_reports.py         # Scheduler-driven report generation
|
|-- public/frontend/                 # Built frontend assets (generated)


frontend/                            # Vue 3 SPA (source)
|
|-- src/
|   |-- pages/ChatView.vue           # Main chat interface
|   |-- components/
|   |   |-- Sidebar.vue              # Conversation list, provider switcher
|   |   |-- ChatHeader.vue           # Conversation header
|   |   |-- ChatMessage.vue          # Message rendering (markdown, charts)
|   |   |-- ChatInput.vue            # Input with @mentions, file upload
|   |   |-- TypingIndicator.vue      # Streaming indicator
|   |-- utils/api.js                 # ChatAPI singleton with CSRF handling
|
|-- vite.config.js                   # Build config with manual chunks
|-- tailwind.config.js               # Tailwind CSS configuration
```

---

## Tool Plugin System

External Frappe apps can register custom tools with the chatbot without modifying this app.

### 1. Create a tool module in your app

```python
# my_app/chatbot_tools/manufacturing.py

from ai_chatbot.tools.registry import register_tool

@register_tool(
    name="get_production_summary",
    category="manufacturing",
    description="Get production order summary for a date range",
    parameters={
        "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
        "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
        "company": {"type": "string", "description": "Company name"},
    },
    doctypes=["Work Order"],
)
def get_production_summary(from_date=None, to_date=None, company=None):
    # Your implementation here
    ...
```

### 2. Register the module in your app's hooks.py

```python
# my_app/hooks.py

ai_chatbot_tool_modules = ["my_app.chatbot_tools.manufacturing"]
```

### 3. Optionally register a new category

If you want your tools grouped under a new category with a toggle in Chatbot Settings:

```python
from ai_chatbot.tools.registry import register_tool_category

register_tool_category("manufacturing", settings_field=None)
# Pass settings_field="enable_manufacturing_tools" if you add
# a corresponding checkbox to Chatbot Settings via customize form.
# If settings_field is None, the category is always enabled.
```

The chatbot will automatically discover and load your tools at runtime. Permission checks are enforced based on the `doctypes` list declared in each tool.

---

## Development

### Frontend

```bash
cd apps/ai_chatbot/frontend

# Install dependencies
npm install

# Start dev server (http://localhost:8080, proxies API to Frappe)
npm run dev

# Production build (outputs to ai_chatbot/public/frontend)
npm run build
```

### Backend

```bash
# Start Frappe development server
bench start

# Run backend tests
bench --site <your-site> run-tests --app ai_chatbot

# Linting
ruff check .
ruff format .

# Or via pre-commit
pre-commit run --all-files
```

### Code Conventions

- **Python**: Tabs for indentation, 110-character line length, double quotes, type hints
- **JavaScript/Vue**: Vue 3 Composition API (`<script setup>`), Tailwind CSS
- **API pattern**: `@frappe.whitelist()` decorators, Frappe ORM (`frappe.qb` / `frappe.get_all`) for database access -- no raw SQL with string interpolation
- **Error handling**: `try/except` with `frappe.log_error()`

### Dependencies

**Python** (runtime): frappe, openai, anthropic, twilio==8.5.0, requests

**Python** (optional, for IDP): pypdf>=4.0, openpyxl>=3.1, python-docx>=1.1

**Frontend**: vue 3, vue-router, marked, highlight.js, lucide-vue-next, tailwindcss, echarts, socket.io-client

---

## Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_OVERVIEW.md](../docs/PROJECT_OVERVIEW.md) | High-level architecture and design decisions |
| [PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md) | Detailed file and directory structure |
| [API.md](../docs/API.md) | Backend API endpoint reference |
| [SAMPLE_USER_PROMPT.md](../docs/SAMPLE_USER_PROMPT.md) | Example prompts organized by category |
| [ENHANCEMENT_ROADMAP.md](../docs/ENHANCEMENT_ROADMAP.md) | Planned features and development phases |

---

## License

MIT License. See [license.txt](../license.txt) for details.
