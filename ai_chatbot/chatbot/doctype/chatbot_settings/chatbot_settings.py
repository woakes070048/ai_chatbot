# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChatbotSettings(Document):
	"""Chatbot Settings DocType Controller"""
	
	def validate(self):
		"""Validate settings before save"""
		# Validate OpenAI settings
		if self.openai_enabled and not self.openai_api_key:
			frappe.throw("OpenAI API Key is required when OpenAI is enabled")
		
		# Validate Claude settings
		if self.claude_enabled and not self.claude_api_key:
			frappe.throw("Claude API Key is required when Claude is enabled")
		
		# At least one provider must be enabled
		if not self.openai_enabled and not self.claude_enabled:
			frappe.throw("At least one AI provider must be enabled")
	
	def on_update(self):
		"""Called after document is saved"""
		# Clear cache when settings are updated
		frappe.cache().delete_value("ai_chatbot_settings")
