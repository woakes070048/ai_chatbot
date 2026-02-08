# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class ChatbotConversation(Document):
	"""Chatbot Conversation DocType Controller"""
	
	def before_insert(self):
		"""Called before document is inserted"""
		# Set timestamps
		self.created_at = datetime.now()
		self.updated_at = datetime.now()
		
		# Set default user if not set
		if not self.user:
			self.user = frappe.session.user
	
	def before_save(self):
		"""Called before document is saved"""
		# Update timestamp
		self.updated_at = datetime.now()
	
	def validate(self):
		"""Validate document before save"""
		# Validate AI provider
		if self.ai_provider not in ["OpenAI", "Claude"]:
			frappe.throw("Invalid AI provider. Must be 'OpenAI' or 'Claude'")
		
		# Check if provider is enabled in settings
		settings = frappe.get_single("Chatbot Settings")
		if self.ai_provider == "OpenAI" and not settings.openai_enabled:
			frappe.throw("OpenAI is not enabled in AI Chatbot Settings")
		elif self.ai_provider == "Claude" and not settings.claude_enabled:
			frappe.throw("Claude is not enabled in AI Chatbot Settings")
	
	def on_trash(self):
		"""Called when document is deleted"""
		# Delete all messages in this conversation
		frappe.db.delete("Chatbot Message", {"conversation": self.name})
	
	def update_message_count(self):
		"""Update the message count for this conversation"""
		count = frappe.db.count("Chatbot Message", {"conversation": self.name})
		self.message_count = count
		self.save(ignore_permissions=True, ignore_version=True)
	
	def update_token_usage(self, tokens):
		"""Add tokens to the total usage"""
		self.total_tokens = (self.total_tokens or 0) + tokens
		self.save(ignore_permissions=True, ignore_version=True)
