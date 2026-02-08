"""
AI Provider Integration Module
Handles OpenAI and Claude API integrations
"""

import frappe
import json
import requests
from typing import Generator, Dict, List, Any


class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self, settings):
        self.settings = settings
    
    def chat_completion(self, messages: List[Dict], tools: List[Dict] = None, stream: bool = False):
        raise NotImplementedError
    
    def validate_settings(self):
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI API Integration"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.api_key = settings.get("openai_api_key")
        self.model = settings.get("openai_model", "gpt-4o")
        self.temperature = settings.get("openai_temperature", 0.7)
        self.max_tokens = settings.get("openai_max_tokens", 4000)
        self.base_url = "https://api.openai.com/v1"
    
    def validate_settings(self):
        if not self.api_key:
            frappe.throw("OpenAI API Key is required")
        return True
    
    def chat_completion(self, messages: List[Dict], tools: List[Dict] = None, stream: bool = False) -> Generator:
        """
        OpenAI Chat Completion with streaming support
        """
        self.validate_settings()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"OpenAI API Error: {str(e)}", "AI Chatbot")
            frappe.throw(f"OpenAI API Error: {str(e)}")
    
    def _handle_stream(self, response) -> Generator:
        """Handle streaming response from OpenAI"""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk['choices'][0].get('delta'):
                            yield chunk
                    except json.JSONDecodeError:
                        continue


class ClaudeProvider(AIProvider):
    """Anthropic Claude API Integration"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.api_key = settings.get("claude_api_key")
        self.model = settings.get("claude_model", "claude-sonnet-4-5-20250929")
        self.temperature = settings.get("claude_temperature", 0.7)
        self.max_tokens = settings.get("claude_max_tokens", 4000)
        self.base_url = "https://api.anthropic.com/v1"
        self.api_version = "2023-06-01"
    
    def validate_settings(self):
        if not self.api_key:
            frappe.throw("Claude API Key is required")
        return True
    
    def chat_completion(self, messages: List[Dict], tools: List[Dict] = None, stream: bool = False) -> Generator:
        """
        Claude Messages API with streaming support
        """
        self.validate_settings()
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }
        
        # Convert OpenAI format to Claude format
        claude_messages = self._convert_messages_to_claude(messages)
        system_message = self._extract_system_message(messages)
        
        payload = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": stream
        }
        
        if system_message:
            payload["system"] = system_message
        
        if tools:
            payload["tools"] = self._convert_tools_to_claude(tools)
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Claude API Error: {str(e)}", "AI Chatbot")
            frappe.throw(f"Claude API Error: {str(e)}")
    
    def _convert_messages_to_claude(self, messages: List[Dict]) -> List[Dict]:
        """Convert OpenAI message format to Claude format"""
        claude_messages = []
        for msg in messages:
            if msg['role'] != 'system':
                claude_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        return claude_messages
    
    def _extract_system_message(self, messages: List[Dict]) -> str:
        """Extract system message from messages list"""
        for msg in messages:
            if msg['role'] == 'system':
                return msg['content']
        return ""
    
    def _convert_tools_to_claude(self, tools: List[Dict]) -> List[Dict]:
        """Convert OpenAI tool format to Claude format"""
        claude_tools = []
        for tool in tools:
            if tool.get('type') == 'function':
                func = tool['function']
                claude_tools.append({
                    'name': func['name'],
                    'description': func.get('description', ''),
                    'input_schema': func.get('parameters', {})
                })
        return claude_tools
    
    def _handle_stream(self, response) -> Generator:
        """Handle streaming response from Claude"""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    try:
                        chunk = json.loads(data)
                        yield chunk
                    except json.JSONDecodeError:
                        continue


def get_ai_provider(provider_name: str):
    """Factory function to get AI provider instance"""
    settings = frappe.get_single("Chatbot Settings")
    
    if provider_name == "OpenAI":
        if not settings.openai_enabled:
            frappe.throw("OpenAI is not enabled in settings")
        return OpenAIProvider(settings.as_dict())
    elif provider_name == "Claude":
        if not settings.claude_enabled:
            frappe.throw("Claude is not enabled in settings")
        return ClaudeProvider(settings.as_dict())
    else:
        frappe.throw(f"Unknown AI provider: {provider_name}")
