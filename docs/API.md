# AI Chatbot — API Documentation

Complete API reference for the AI Chatbot application.

## Base URLs

```
/api/method/ai_chatbot.api.chat          # Core chat endpoints
/api/method/ai_chatbot.api.streaming     # Streaming endpoint
/api/method/ai_chatbot.api.files         # File upload endpoint
/api/method/ai_chatbot.api.export        # PDF export endpoints
```

## Authentication

All endpoints require Frappe session authentication. Include CSRF token in POST requests:

```javascript
headers: {
  'Content-Type': 'application/json',
  'X-Frappe-CSRF-Token': window.csrf_token
}
```

---

## Chat Endpoints (`api.chat`)

### 1. create_conversation

Creates a new chat conversation.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | No | Conversation title (default: "New Chat") |
| ai_provider | string | No | "OpenAI", "Claude", or "Gemini" (default: from settings) |

**Response**:
```json
{
  "success": true,
  "conversation_id": "CHAT-00001",
  "data": {
    "name": "CHAT-00001",
    "title": "New Chat",
    "user": "user@example.com",
    "ai_provider": "OpenAI",
    "status": "Active",
    "created_at": "2026-01-29 12:00:00",
    "updated_at": "2026-01-29 12:00:00",
    "message_count": 0,
    "total_tokens": 0
  }
}
```

---

### 2. get_conversations

Retrieves all conversations for the current user, ordered by last activity.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| limit | integer | No | Maximum results (default: 20) |

**Response**:
```json
{
  "success": true,
  "conversations": [
    {
      "name": "CHAT-00001",
      "title": "Product Discussion",
      "ai_provider": "OpenAI",
      "status": "Active",
      "created_at": "2026-01-29 12:00:00",
      "updated_at": "2026-01-29 12:30:00",
      "message_count": 15
    }
  ]
}
```

---

### 3. get_conversation_messages

Retrieves all messages for a specific conversation. Validates conversation ownership.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID (e.g. "CHAT-00001") |

**Response**:
```json
{
  "success": true,
  "messages": [
    {
      "name": "MSG-00001",
      "role": "user",
      "content": "What are our sales this month?",
      "timestamp": "2026-01-29 12:00:00",
      "tokens_used": 0,
      "tool_calls": null,
      "tool_results": null,
      "attachments": null
    },
    {
      "name": "MSG-00002",
      "role": "assistant",
      "content": "Based on the sales data...",
      "timestamp": "2026-01-29 12:00:05",
      "tokens_used": 450,
      "tool_calls": "[{\"function\": {\"name\": \"get_sales_analytics\", ...}}]",
      "tool_results": "[{\"success\": true, \"data\": {...}}]",
      "attachments": null
    }
  ]
}
```

---

### 4. send_message

Sends a message and gets an AI response. Supports both synchronous and streaming modes.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID |
| message | string | Yes | User message text |
| stream | boolean | No | Enable streaming (default: false). When true, delegates to the streaming API. |

**Response (non-streaming)**:
```json
{
  "success": true,
  "message": "Based on the sales data, your total revenue this month is ₹5,00,000...",
  "tokens_used": 450,
  "tool_calls": [
    {
      "function": {
        "name": "get_sales_analytics",
        "arguments": "{\"from_date\":\"2026-01-01\",\"to_date\":\"2026-01-31\"}"
      }
    }
  ],
  "tool_results": [
    {
      "success": true,
      "data": {
        "total_revenue": 500000,
        "invoice_count": 120,
        "company": "My Company",
        "currency": "INR",
        "echart_option": {...}
      }
    }
  ]
}
```

**Response (streaming)**: Returns immediately with `stream_id`. Tokens delivered via Socket.IO (see Streaming section below).
```json
{
  "success": true,
  "stream_id": "abc12345"
}
```

---

### 5. delete_conversation

Deletes a conversation and all its messages. Validates ownership.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID |

**Response**:
```json
{
  "success": true
}
```

---

### 6. update_conversation_title

Updates the title of a conversation.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID |
| title | string | Yes | New title |

**Response**:
```json
{
  "success": true
}
```

---

### 7. set_conversation_language

Sets or resets the response language for a specific conversation.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID |
| language | string | No | Language name (e.g. "Hindi", "Spanish"). Empty to reset to default. |

**Response**:
```json
{
  "success": true
}
```

---

### 8. get_settings

Retrieves chatbot configuration settings (public-facing subset).

**Method**: POST

**Parameters**: None

**Response**:
```json
{
  "success": true,
  "settings": {
    "ai_provider": "OpenAI",
    "model": "gpt-4o",
    "enable_streaming": true,
    "enable_crm_tools": true,
    "enable_sales_tools": true,
    "enable_purchase_tools": true,
    "enable_finance_tools": true,
    "enable_inventory_tools": true,
    "enable_hrms_tools": true,
    "enable_write_operations": false,
    "enable_idp_tools": true,
    "enable_predictive_tools": true,
    "enable_agent_orchestration": true,
    "response_language": "English"
  }
}
```

---

### 9. get_sample_prompts

Returns categorized sample prompts for the Help Modal.

**Method**: POST

**Parameters**: None

**Response**:
```json
{
  "success": true,
  "prompts": {
    "Sales": ["What is the total sales this month?", "Show top 10 customers by revenue", ...],
    "Finance": ["Show me the CFO dashboard", "Show profit and loss for this fiscal year", ...],
    ...
  }
}
```

---

### 10. search_conversations

Searches conversations by title or content.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | Yes | Search text |
| limit | integer | No | Maximum results (default: 20) |

**Response**:
```json
{
  "success": true,
  "conversations": [...]
}
```

---

### 11. get_mention_values

Returns autocomplete values for the @mention system.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mention_type | string | Yes | Category: company, period, cost_center, department, warehouse, customer, item, accounting_dimension |
| search_term | string | No | Filter text |
| company | string | No | Company context (for cost_center, department, warehouse filtering) |

**Response**:
```json
{
  "success": true,
  "values": [
    {"value": "Tara Technologies", "description": "Default company"},
    {"value": "Tara Technologies (Demo)", "description": ""}
  ]
}
```

---

## Streaming Endpoint (`api.streaming`)

### send_message_streaming

Enqueues a background job that streams AI response tokens via Frappe Realtime (Socket.IO). The HTTP response returns immediately with a `stream_id`.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID |
| message | string | Yes | User message text |

**HTTP Response** (immediate):
```json
{
  "success": true,
  "stream_id": "abc12345"
}
```

**Socket.IO Events** (delivered asynchronously):

| Event | Payload | Description |
|-------|---------|-------------|
| `ai_chat_stream_start` | `{conversation_id, stream_id}` | Stream has started |
| `ai_chat_token` | `{conversation_id, stream_id, content}` | Text token chunk |
| `ai_chat_tool_call` | `{conversation_id, stream_id, tool_name, tool_arguments}` | Tool call initiated |
| `ai_chat_tool_result` | `{conversation_id, stream_id, tool_name, result}` | Tool execution result |
| `ai_chat_process_step` | `{conversation_id, stream_id, step}` | Processing status label |
| `ai_chat_stream_end` | `{conversation_id, stream_id, content, tokens_used, tool_calls}` | Stream complete |
| `ai_chat_error` | `{conversation_id, stream_id, error}` | Error during streaming |
| `ai_chat_agent_plan` | `{conversation_id, stream_id, plan}` | Multi-agent plan steps |
| `ai_chat_agent_step_start` | `{conversation_id, stream_id, step_id, description}` | Agent step started |
| `ai_chat_agent_step_result` | `{conversation_id, stream_id, step_id, status, summary}` | Agent step completed |

---

## File Upload Endpoint (`api.files`)

### upload_chat_file

Uploads a file attached to a conversation. Files are stored as private Frappe File documents.

**Method**: POST (multipart/form-data)

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID |
| file | File | Yes | The file to upload (via form data) |

**Allowed MIME types**: JPEG, PNG, GIF, WebP, PDF, plain text, CSV, XLSX, DOCX

**Max file size**: 10 MB

**Response**:
```json
{
  "success": true,
  "file_url": "/private/files/invoice.pdf",
  "file_name": "invoice.pdf",
  "mime_type": "application/pdf",
  "is_image": false,
  "base64": null
}
```

For image files, `is_image` is true and `base64` contains the data URI for Vision API use.

---

## PDF Export Endpoints (`api.export`)

### export_message_pdf

Exports a single assistant message as a styled PDF.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message_name | string | Yes | Message ID (e.g. "MSG-00001") |

**Response**:
```json
{
  "success": true,
  "file_url": "/private/files/chat_export_20260129.pdf"
}
```

---

### export_conversation_pdf

Exports an entire conversation as a styled PDF transcript.

**Method**: POST

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string | Yes | Conversation ID |

**Response**:
```json
{
  "success": true,
  "file_url": "/private/files/conversation_CHAT-00001.pdf"
}
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

**Common Error Codes**:
- `400` — Bad Request (invalid parameters)
- `401` — Unauthorized (not logged in)
- `403` — Forbidden (insufficient permissions or conversation not owned by user)
- `404` — Not Found (conversation/message does not exist)
- `500` — Internal Server Error

---

## Best Practices

### Error Handling
Always wrap API calls in try-catch:

```javascript
try {
  const response = await chatAPI.sendMessage(conversationId, message);
  if (response.success) {
    // Handle success
  }
} catch (error) {
  console.error('API Error:', error);
}
```

### Loading States
Show loading indicators during API calls:

```javascript
isLoading.value = true;
try {
  await chatAPI.sendMessage(...);
} finally {
  isLoading.value = false;
}
```

### Optimistic Updates
Update UI immediately, then sync with server:

```javascript
messages.value.push(userMessage);
const response = await chatAPI.sendMessage(...);
messages.value.push(response.message);
```

---

## SDK Examples

### JavaScript (Frontend)

```javascript
import { chatAPI } from './utils/api';

// Create conversation
const conv = await chatAPI.createConversation('My Chat', 'OpenAI');

// Send message (non-streaming)
const response = await chatAPI.sendMessage(conv.conversation_id, 'What are my sales?');

// Send message (streaming) — tokens arrive via Socket.IO
await chatAPI.sendMessageStreaming(conv.conversation_id, 'Show the CFO dashboard');

// Upload a file
const fileData = await chatAPI.uploadFile(conv.conversation_id, fileObject);

// Export message as PDF
const pdf = await chatAPI.exportMessagePdf('MSG-00001');

// Get @mention values
const companies = await chatAPI.getMentionValues('company', 'Tara');
```

### Python (Server-side)

```python
import frappe

# Create conversation
conversation = frappe.get_doc({
    "doctype": "Chatbot Conversation",
    "title": "My Chat",
    "user": frappe.session.user,
    "ai_provider": "OpenAI"
})
conversation.insert()

# Send message
from ai_chatbot.api.chat import send_message
response = send_message(conversation.name, "What are the current bank balances?")
```

---

**API Version**: 2.0
**Last Updated**: April 2026
