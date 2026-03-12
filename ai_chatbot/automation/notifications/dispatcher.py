# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Notification Dispatcher

Sends email notifications for scheduled reports. Uses Frappe's
email infrastructure with optional sender (Email Account) override.
"""

from __future__ import annotations

import frappe


def dispatch(
	subject: str,
	html_message: str,
	recipients: list[dict],
	sender: str | None = None,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	attachments: list[dict] | None = None,
) -> None:
	"""Send an email notification to all recipients.

	Args:
		subject: Email subject line.
		html_message: HTML email body.
		recipients: List of recipient dicts with "recipient_email" and optional "user" keys.
		sender: Optional Email Account name to use as the sender.
			If None, Frappe uses the default outgoing email account.
		reference_doctype: Optional DocType reference for email linking.
		reference_name: Optional document name reference for email linking.
		attachments: Optional list of attachment dicts with "fname" and "fcontent" keys.
	"""
	if not recipients:
		frappe.log_error("No recipients specified for notification", "AI Chatbot Automation")
		return

	email_list = [r.get("recipient_email") for r in recipients if r.get("recipient_email")]
	if not email_list:
		frappe.log_error("No valid email addresses in recipients", "AI Chatbot Automation")
		return

	from ai_chatbot.automation.notifications.channels.email import send_email

	send_email(
		subject=subject,
		html_message=html_message,
		recipients=email_list,
		sender=sender,
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		attachments=attachments,
	)
