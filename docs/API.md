# AI Chatbot - API Documentation

Complete API reference for the AI Chatbot application.

## Base URL

All API endpoints are prefixed with:
```
/api/method/ai_chatbot.api.chat
```

## Authentication

All endpoints require Frappe session authentication. Include CSRF token in POST requests:

```javascript
headers: {
  'X-Frappe-CSRF-Token': window.csrf_token
}
```

## Endpoints

### 1. Create Conversation

Creates a new chat conversation.

**Endpoint**: `create_conversation`

**Method**: POST

**Parameters**:
```json
{
  "title": "string",           // Conversation title
  "ai_provider": "string"      // "OpenAI" or "Claude"
}
```

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
    "created_at": "2024-01-29 12:00:00",
    "updated_at": "2024-01-29 12:00:00",
    "message_count": 0,
    "total_tokens": 0
  }
}
```

**Example**:
```javascript
const response = await fetch('/api/method/ai_chatbot.api.chat.create_conversation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Frappe-CSRF-Token': window.csrf_token
  },
  body: JSON.stringify({
    title: 'My New Chat',
    ai_provider: 'OpenAI'
  })
});
```

---

### 2. Get Conversations

Retrieves all conversations for the current user.

**Endpoint**: `get_conversations`

**Method**: POST

**Parameters**:
```json
{
  "limit": 20  // Optional, default: 20
}
```

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
      "created_at": "2024-01-29 12:00:00",
      "updated_at": "2024-01-29 12:30:00",
      "message_count": 15
    }
  ]
}
```

---

### 3. Get Conversation Messages

Retrieves all messages for a specific conversation.

**Endpoint**: `get_conversation_messages`

**Method**: POST

**Parameters**:
```json
{
  "conversation_id": "string"  // Conversation ID
}
```

**Response**:
```json
{
  "success": true,
  "messages": [
    {
      "name": "MSG-00001",
      "role": "user",
      "content": "Hello, how are you?",
      "timestamp": "2024-01-29 12:00:00",
      "tokens_used": 0,
      "tool_calls": null
    },
    {
      "name": "MSG-00002",
      "role": "assistant",
      "content": "I'm doing well, thank you!",
      "timestamp": "2024-01-29 12:00:05",
      "tokens_used": 150,
      "tool_calls": null
    }
  ]
}
```

---

### 4. Send Message

Sends a message and gets AI response.

**Endpoint**: `send_message`

**Method**: POST

**Parameters**:
```json
{
  "conversation_id": "string",  // Conversation ID
  "message": "string",          // User message
  "stream": false               // Optional, default: false
}
```

**Response**:
```json
{
  "success": true,
  "message": "AI response text here...",
  "tokens_used": 350
}
```

**With Tool Calls**:
```json
{
  "success": true,
  "message": "Based on the sales data, here's the analysis...",
  "tokens_used": 450,
  "tool_calls": [
    {
      "function": {
        "name": "get_sales_analytics",
        "arguments": "{\"from_date\":\"2024-01-01\",\"to_date\":\"2024-01-31\"}"
      }
    }
  ]
}
```

---

### 5. Delete Conversation

Deletes a conversation and all its messages.

**Endpoint**: `delete_conversation`

**Method**: POST

**Parameters**:
```json
{
  "conversation_id": "string"  // Conversation ID
}
```

**Response**:
```json
{
  "success": true
}
```

---

### 6. Update Conversation Title

Updates the title of a conversation.

**Endpoint**: `update_conversation_title`

**Method**: POST

**Parameters**:
```json
{
  "conversation_id": "string",  // Conversation ID
  "title": "string"             // New title
}
```

**Response**:
```json
{
  "success": true
}
```

---

### 7. Get Settings

Retrieves chatbot configuration settings.

**Endpoint**: `get_settings`

**Method**: POST

**Parameters**: None

**Response**:
```json
{
  "success": true,
  "settings": {
    "openai_enabled": true,
    "claude_enabled": true,
    "tools_enabled": {
      "crm": true,
      "sales": true,
      "purchase": true,
      "finance": true,
      "inventory": true
    }
  }
}
```

---

## ERPNext Tools

The chatbot can automatically call these tools when relevant to the conversation.

### CRM Tools

#### get_lead_statistics
Get statistics about leads including count, status breakdown, and conversion rates.

**Parameters**:
```json
{
  "from_date": "2024-01-01",  // Optional
  "to_date": "2024-01-31"     // Optional
}
```

**Returns**:
```json
{
  "total_leads": 150,
  "status_breakdown": {
    "Open": 50,
    "Converted": 80,
    "Lost": 20
  },
  "period": {
    "from": "2024-01-01",
    "to": "2024-01-31"
  }
}
```

#### get_opportunity_pipeline
Get sales opportunity pipeline with stages and values.

**Parameters**:
```json
{
  "status": "Open"  // Optional: "Open", "Converted", "Lost"
}
```

**Returns**:
```json
{
  "opportunities": [...],
  "total_value": 1250000,
  "count": 45
}
```

### Sales Tools

#### get_sales_analytics
Get sales analytics including revenue, orders, and growth trends.

**Parameters**:
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-01-31",
  "customer": "ABC Corp"  // Optional
}
```

**Returns**:
```json
{
  "total_revenue": 500000,
  "invoice_count": 120,
  "average_order_value": 4166.67,
  "period": {
    "from": "2024-01-01",
    "to": "2024-01-31"
  }
}
```

#### get_top_customers
Get top customers by revenue.

**Parameters**:
```json
{
  "limit": 10,
  "from_date": "2024-01-01"  // Optional
}
```

**Returns**:
```json
{
  "top_customers": [
    {
      "customer": "ABC Corp",
      "total_revenue": 150000,
      "order_count": 25
    }
  ]
}
```

### Purchase Tools

#### get_purchase_analytics
Get purchase analytics including spending, orders, and supplier performance.

**Parameters**:
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

#### get_supplier_performance
Analyze supplier performance metrics.

**Parameters**:
```json
{
  "supplier": "XYZ Supplies"  // Optional
}
```

### Finance Tools

#### get_financial_summary
Get financial summary including P&L, balance sheet highlights.

**Parameters**:
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-01-31"
}
```

**Returns**:
```json
{
  "revenue": 500000,
  "expenses": 350000,
  "profit": 150000,
  "period": {
    "from": "2024-01-01",
    "to": "2024-01-31"
  }
}
```

#### get_cash_flow_analysis
Analyze cash flow patterns and trends.

**Parameters**:
```json
{
  "months": 6  // Number of months to analyze
}
```

### Inventory Tools

#### get_inventory_summary
Get inventory summary including stock levels, valuation.

**Parameters**:
```json
{
  "warehouse": "Main Warehouse"  // Optional
}
```

**Returns**:
```json
{
  "unique_items": 500,
  "total_quantity": 15000,
  "total_value": 2500000,
  "warehouse": "Main Warehouse"
}
```

#### get_low_stock_items
Get items with low stock levels.

**Parameters**:
```json
{
  "threshold_days": 30  // Days of stock threshold
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
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (conversation/message doesn't exist)
- `500` - Internal Server Error

---

## Rate Limiting

API requests are rate-limited per user:
- **Conversations**: 60 per hour
- **Messages**: 120 per hour
- **Tool Calls**: 300 per hour

---

## Best Practices

### 1. Error Handling
Always wrap API calls in try-catch:

```javascript
try {
  const response = await chatAPI.sendMessage(conversationId, message);
  if (response.success) {
    // Handle success
  }
} catch (error) {
  console.error('API Error:', error);
  // Show user-friendly error message
}
```

### 2. Loading States
Show loading indicators during API calls:

```javascript
isLoading.value = true;
try {
  await chatAPI.sendMessage(...);
} finally {
  isLoading.value = false;
}
```

### 3. Optimistic Updates
Update UI immediately, then sync with server:

```javascript
// Add message to UI
messages.value.push(userMessage);

// Send to server
const response = await chatAPI.sendMessage(...);

// Update with server response
messages.value.push(response.message);
```

### 4. Caching
Cache conversation lists and settings:

```javascript
const conversationsCache = ref(null);
const cacheTimeout = 5 * 60 * 1000; // 5 minutes

async function getConversations() {
  if (conversationsCache.value && Date.now() - conversationsCache.timestamp < cacheTimeout) {
    return conversationsCache.value;
  }
  
  const response = await chatAPI.getConversations();
  conversationsCache.value = response.conversations;
  conversationsCache.timestamp = Date.now();
  
  return response.conversations;
}
```

---

## Webhooks (Future)

Webhook support for real-time updates (planned):

```json
{
  "event": "message.created",
  "data": {
    "conversation_id": "CHAT-00001",
    "message": {...}
  },
  "timestamp": "2024-01-29T12:00:00Z"
}
```

---

## SDK Examples

### JavaScript/TypeScript

```javascript
import { chatAPI } from './utils/api';

// Create conversation
const conversation = await chatAPI.createConversation('My Chat', 'OpenAI');

// Send message
const response = await chatAPI.sendMessage(
  conversation.conversation_id,
  'What are my sales figures?'
);

// Get messages
const messages = await chatAPI.getConversationMessages(conversation.conversation_id);
```

### Python

```python
import frappe

# Create conversation
conversation = frappe.get_doc({
    "doctype": "AI Chat Conversation",
    "title": "My Chat",
    "user": frappe.session.user,
    "ai_provider": "OpenAI"
})
conversation.insert()

# Send message
from ai_chatbot.api.chat import send_message
response = send_message(conversation.name, "Hello!")
```

---

## Support

For API issues or questions:
- **Documentation**: See README.md
- **GitHub Issues**: Report bugs
- **Email**: api-support@yourcompany.com

---

**API Version**: 1.0.0
**Last Updated**: January 2026
