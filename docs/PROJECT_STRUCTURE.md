# AI Chatbot - Project Structure

This document explains the complete file structure of the AI Chatbot application following Frappe framework specifications.

## 📁 Root Directory Structure

```
ai_chatbot/                                # Root app directory
├── frontend/                              # Modern UI source (Vue + Tailwind)
├── ai_chatbot/                            # Main Python package
├── requirements.txt                       # Python dependencies
├── package.json                           # Node.js dependencies
├── setup.sh                               # Installation script
├── README.md                              # Main documentation
├── LICENSE                                # MIT License
├── .gitignore                             # Git ignore rules
├── INSTALLATION.md                        # Installation guide
├── API.md                                 # API documentation
├── QUICKSTART.md                          # Quick start guide
└── PROJECT_OVERVIEW.md                    # Project overview
```

## 🎨 Frontend Directory (`frontend/`)

The frontend is built with Vue 3, Vite, and Tailwind CSS.

```
frontend/
├── src/
│   ├── components/                        # Reusable Vue components
│   │   ├── Sidebar.vue                    # Conversation list sidebar
│   │   ├── ChatHeader.vue                 # Chat header with controls
│   │   ├── ChatMessage.vue                # Individual message display
│   │   ├── ChatInput.vue                  # Message input area
│   │   └── TypingIndicator.vue            # Loading animation
│   │
│   ├── pages/                             # View/Page components
│   │   └── ChatView.vue                   # Main chat interface
│   │
│   ├── utils/
│   │   └── api.js                         # API client utilities
│   │
│   ├── App.vue                            # Root Vue component
│   ├── main.js                            # Entry point
│   └── style.css                          # Global styles (Tailwind)
│
├── index.html                             # SPA entry point
├── tailwind.config.js                     # Tailwind configuration
├── vite.config.js                         # Vite build configuration
└── package.json                           # Frontend dependencies
```

### Frontend Technologies
- **Framework**: Vue 3 (Composition API)
- **UI Library**: Frappe UI
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Markdown**: marked.js
- **Syntax Highlighting**: highlight.js
- **Charts**: Chart.js + vue-chartjs
- **Icons**: Lucide Vue

## 🐍 Backend Directory (`ai_chatbot/`)

The backend follows Frappe's standard Python package structure.

```
ai_chatbot/
├── __init__.py                            # Package initialization (version)
├── hooks.py                               # App metadata & event hooks
├── modules.txt                            # Module list
├── patches.txt                            # Database migration patches
│
├── config/                                # App configuration
│   └── __init__.py
│
├── ai_chatbot/                            # Main module directory
│   ├── __init__.py
│   │
│   ├── doctype/                           # DocType definitions
│   │   ├── __init__.py
│   │   │
│   │   ├── ai_chatbot_settings/           # Settings DocType
│   │   │   ├── __init__.py
│   │   │   ├── ai_chatbot_settings.json   # Schema definition
│   │   │   ├── ai_chatbot_settings.py     # Python controller
│   │   │   └── ai_chatbot_settings.js     # Client-side logic
│   │   │
│   │   ├── ai_chat_conversation/          # Conversation DocType
│   │   │   ├── __init__.py
│   │   │   ├── ai_chat_conversation.json
│   │   │   ├── ai_chat_conversation.py
│   │   │   └── ai_chat_conversation.js
│   │   │
│   │   └── ai_chat_message/               # Message DocType
│   │       ├── __init__.py
│   │       ├── ai_chat_message.json
│   │       ├── ai_chat_message.py
│   │       └── ai_chat_message.js
│   │
│   ├── page/                              # Custom pages
│   │   └── __init__.py
│   │
│   └── report/                            # Custom reports
│       └── __init__.py
│
├── api/                                   # API endpoints
│   ├── __init__.py
│   └── chat.py                            # Chat API methods
│
├── utils/                                 # Utility modules
│   ├── __init__.py
│   ├── ai_providers.py                    # OpenAI & Claude integration
│   └── erpnext_tools.py                   # Business intelligence tools
│
├── public/                                # Static assets
│   ├── __init__.py
│   ├── css/                               # Stylesheets
│   ├── js/                                # JavaScript files
│   └── img/                               # Images
│
├── templates/                             # Jinja templates
│   ├── __init__.py
│   ├── includes/                          # Template includes
│   └── pages/                             # Page templates
│
└── www/                                   # Public portal pages
    └── __init__.py
```

## 📋 Key Files Explained

### Root Level

#### `requirements.txt`
Python dependencies for the app:
- frappe
- requests (for API calls)

#### `package.json`
Node.js dependencies and build scripts for asset bundling.

#### `setup.sh`
Automated installation script that:
- Installs Python dependencies
- Installs app to Frappe site
- Runs database migrations
- Installs and builds frontend
- Restarts services

#### `.gitignore`
Excludes:
- Python cache files
- Node modules
- Build artifacts
- IDE files
- Environment files
- Secrets

### Backend Core Files

#### `ai_chatbot/__init__.py`
```python
__version__ = '1.0.0'
```
Defines the app version.

#### `ai_chatbot/hooks.py`
Main configuration file containing:
- App metadata (name, title, description)
- Event hooks
- Integration points
- Custom settings

#### `ai_chatbot/modules.txt`
```
AI Chatbot
```
Lists modules defined in the app.

#### `ai_chatbot/patches.txt`
Empty file for database migration patches (used by Frappe's migration system).

### DocTypes

Each DocType has three key files:

1. **`.json`** - Schema definition (fields, permissions, metadata)
2. **`.py`** - Server-side controller (business logic, validation)
3. **`.js`** - Client-side script (form behavior, UI logic)

### API Layer

#### `ai_chatbot/api/chat.py`
RESTful API endpoints:
- `create_conversation` - Create new chat
- `get_conversations` - List conversations
- `get_conversation_messages` - Get messages
- `send_message` - Send message & get AI response
- `delete_conversation` - Delete chat
- `update_conversation_title` - Rename chat
- `get_settings` - Fetch configuration

All methods are decorated with `@frappe.whitelist()` to expose them as API endpoints.

### Utilities

#### `ai_chatbot/utils/ai_providers.py`
AI provider integration:
- `OpenAIProvider` - OpenAI API wrapper
- `ClaudeProvider` - Claude API wrapper
- `get_ai_provider()` - Factory function
- Streaming support
- Error handling

#### `ai_chatbot/utils/erpnext_tools.py`
Business intelligence tools:
- CRM: Leads, opportunities
- Sales: Analytics, customers
- Purchase: Spending, suppliers
- Finance: P&L, cash flow
- Inventory: Stock levels, alerts

## 🔄 Data Flow

```
User Input (Frontend)
    ↓
Vue Component State
    ↓
API Client (utils/api.js)
    ↓
Frappe REST API (api/chat.py)
    ↓
AI Provider (utils/ai_providers.py)
    ↓
OpenAI/Claude API
    ↓
ERPNext Tools (if needed)
    ↓
Database (via DocTypes)
    ↓
Response to Frontend
    ↓
Markdown Rendering & Display
```

## 🚀 Build Process

### Development
```bash
# Frontend dev server
cd frontend
npm run dev
# Runs on http://localhost:8080

# Backend (Frappe)
bench start
```

### Production Build
```bash
# Build frontend
cd frontend
npm run build
# Outputs to ai_chatbot/public/frontend/

# Rebuild app
bench build --app ai_chatbot

# Restart
bench restart
```

## 📦 Installation Flow

1. **Clone/Copy app** to `~/frappe-bench/apps/`
2. **Run setup script**: `./setup.sh`
3. **Configure**: Add API keys in Settings
4. **Access**: Navigate to chatbot page

## 🔧 Configuration Files

### Frontend
- `vite.config.js` - Build configuration
- `tailwind.config.js` - Styling configuration
- `package.json` - Dependencies

### Backend
- `hooks.py` - App hooks
- `modules.txt` - Module list
- `requirements.txt` - Python packages

## 📊 Database Schema

### AI Chatbot Settings (Single DocType)
- Provider configurations
- API keys (encrypted)
- Model settings
- Tool preferences

### AI Chat Conversation
- ID, title, user
- AI provider, model
- Status, timestamps
- Message count, token usage

### AI Chat Message
- Conversation reference
- Role (user/assistant)
- Content
- Timestamp
- Token usage
- Tool calls
- Attachments

## 🔐 Security Considerations

- API keys stored encrypted in database
- User isolation (users only see their conversations)
- CSRF protection on all POST requests
- Input sanitization
- Rate limiting
- Role-based permissions

## 📈 Performance

- Frontend: Vue 3 reactivity for optimal updates
- Backend: Frappe ORM with caching
- Database: Indexed fields for fast queries
- Assets: Minified and bundled
- Images: Optimized serving

## 🧪 Testing

```bash
# Backend tests
bench --site site-name run-tests ai_chatbot

# Frontend tests
cd frontend
npm run test
```

## 📚 Documentation Files

- `README.md` - Main overview
- `INSTALLATION.md` - Detailed setup
- `API.md` - API reference
- `QUICKSTART.md` - Quick guide
- `PROJECT_OVERVIEW.md` - Architecture
- `PROJECT_STRUCTURE.md` - This file

---

**Note**: This structure follows Frappe framework specifications for proper app organization, ensuring compatibility with Frappe's build system, migration tools, and deployment processes.
