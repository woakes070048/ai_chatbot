# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Email Notification Channel

Sends HTML email notifications via frappe.sendmail().
SMTP configuration is managed by Frappe's Email Account settings.
"""

from __future__ import annotations

import frappe


def send_email(
	subject: str,
	html_message: str,
	recipients: list[str],
	sender: str | None = None,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	attachments: list[dict] | None = None,
) -> None:
	"""Send an HTML email via Frappe's email infrastructure.

	Args:
		subject: Email subject line.
		html_message: HTML body content.
		recipients: List of email addresses.
		sender: Optional Email Account name. When provided, the email is
			sent from this account's address. If None, Frappe uses the
			default outgoing email account.
		reference_doctype: Optional DocType for email linking.
		reference_name: Optional document name for email linking.
		attachments: Optional list of attachment dicts with "fname" and "fcontent" keys.
	"""
	if not recipients:
		return

	kwargs: dict = {
		"recipients": recipients,
		"subject": subject,
		"message": html_message,
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"now": True,
	}

	if sender:
		# Resolve sender email address from Email Account
		sender_email = frappe.db.get_value("Email Account", sender, "email_id")
		if sender_email:
			kwargs["sender"] = sender_email

	if attachments:
		kwargs["attachments"] = attachments

	frappe.sendmail(**kwargs)
