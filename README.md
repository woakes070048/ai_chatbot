# AI Chatbot Application for Frappe/ERPNext

> A modern, feature-rich AI chatbot application built with Frappe framework and Frappe UI, featuring OpenAI and Claude integration with powerful ERPNext business intelligence tools.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Frappe](https://img.shields.io/badge/Frappe-v15+-orange.svg)](https://frappeframework.com/)
[![ERPNext](https://img.shields.io/badge/ERPNext-v15+-green.svg)](https://erpnext.com/)

## 🌟 Features

### Core Features
- **Beautiful Modern UI**: Professional, polished design with smooth animations
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Chat**: Smooth conversation experience with auto-scroll
- **Markdown Support**: Rich markdown rendering with syntax highlighting
- **Code Highlighting**: Professional code blocks with highlight.js
- **Tables & Charts**: Render data tables and charts inline
- **Multi-Provider AI**: Support for both OpenAI and Claude
- **Conversation Management**: Create, view, and delete conversations
- **ERPNext Integration**: Built-in business intelligence tools

### AI Providers
- **OpenAI**: GPT-4o, GPT-4-Turbo, GPT-3.5-Turbo
- **Claude**: Opus 4.5, Sonnet 4.5, Haiku 4.5

### ERPNext Tools
The chatbot includes intelligent tools for:
- **CRM**: Lead statistics, opportunity pipeline
- **Sales**: Revenue analytics, top customers
- **Purchase**: Spending analysis, supplier performance
- **Finance**: P&L summary, cash flow analysis
- **Inventory**: Stock levels, low stock alerts

## 📦 Installation

### Prerequisites
- Frappe Bench setup
- Node.js 18+ and npm/yarn
- ERPNext (for business tools)
- OpenAI and/or Claude API keys

# AI Chatbot Application for Frappe/ERPNext

A modern, feature-rich AI chatbot application built with Frappe framework and Frappe UI, featuring OpenAI and Claude integration with powerful ERPNext business intelligence tools.

## 🌟 Features

### Core Features
- **Beautiful Modern UI**: Professional, polished design with smooth animations
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Chat**: Smooth conversation experience with auto-scroll
- **Markdown Support**: Rich markdown rendering with syntax highlighting
- **Code Highlighting**: Professional code blocks with highlight.js
- **Tables & Charts**: Render data tables and charts inline
- **Multi-Provider AI**: Support for both OpenAI and Claude
- **Conversation Management**: Create, view, and delete conversations
- **ERPNext Integration**: Built-in business intelligence tools

### AI Providers
- **OpenAI**: GPT-4o, GPT-4-Turbo, GPT-3.5-Turbo
- **Claude**: Opus 4.5, Sonnet 4.5, Haiku 4.5

### ERPNext Tools
The chatbot includes intelligent tools for:
- **CRM**: Lead statistics, opportunity pipeline
- **Sales**: Revenue analytics, top customers
- **Purchase**: Spending analysis, supplier performance
- **Finance**: P&L summary, cash flow analysis
- **Inventory**: Stock levels, low stock alerts

## 📦 Installation

### Prerequisites
- Frappe Bench setup
- Node.js 18+ and npm/yarn
- ERPNext (for business tools)
- OpenAI and/or Claude API keys

### Quick Install

```bash
# 1. Navigate to your Frappe bench
cd ~/frappe-bench

# 2. Get the app
bench get-app https://github.com/sanjay-kumar001/ai_chatbot.git

# 3. Install on your site
bench --site your-site-name install-app ai_chatbot

# 4. Configure AI provider (OpenAI or Claude)
# Go to: ERPNext → AI Chatbot Settings → Add API Key

# 5. Enable tools
# Go to: AI Chatbot Settings → Enable desired tool categories

# 6. Start using!
# Access chatbot at: https://your-site-name/ai-chatbot
```


For detailed installation instructions, see [INSTALLATION.md](./INSTALLATION.md)

## 🔧 Configuration

Navigate to **AI Chatbot Settings** in Frappe Desk:

1. **Enable AI Provider** (OpenAI or Claude)
2. **Add API Key**
3. **Select Model**
4. **Configure Parameters** (temperature, max tokens)
5. **Enable ERPNext Tools** (optional)

## 💻 Development

### Frontend Development

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:8080
```

### Backend Development

```bash
bench start

# Run tests
bench --site your-site.local run-tests ai_chatbot
```

## 📚 Documentation

- [Installation Guide](./INSTALLATION.md)
- [API Documentation](./API.md)
- [Quick Start](./QUICKSTART.md)
- [Project Overview](./PROJECT_OVERVIEW.md)

## 🏗️ Project Structure

```
ai_chatbot/
├── frontend/                  # Vue 3 + Tailwind UI
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   └── pages/             # View components
│   └── package.json
├── ai_chatbot/                # Main Python package
│   ├── ai_chatbot/            # Module directory
│   │   └── doctype/           # DocType definitions
│   ├── api/                   # API endpoints
│   ├── utils/                 # Utility modules
│   ├── public/                # Static assets
│   └── hooks.py               # App configuration
└── requirements.txt
```

## 🚀 Usage

1. Open Frappe Desk
2. Navigate to **AI Chatbot**
3. Click **New Chat**
4. Start conversing!

Example queries:
- "What are my sales figures for last month?"
- "Show me top 10 customers by revenue"
- "Analyze cash flow for Q1"

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Open pull request

## 📄 License

MIT License - See LICENSE file

## 📞 Support

- **Documentation**: See docs folder
- **Issues**: GitHub Issues
- **Email**: sanjay.kumar001@gmail.com

---

**Built with Claude.AI by Sanjay Kumar for the Frappe/ERPNext Community**

Version: 1.0.0
