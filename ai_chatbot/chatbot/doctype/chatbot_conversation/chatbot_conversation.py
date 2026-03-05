# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document


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
		valid_providers = ("OpenAI", "Claude", "Gemini")
		if self.ai_provider not in valid_providers:
			frappe.throw(f"Invalid AI provider. Must be one of: {', '.join(valid_providers)}")

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
