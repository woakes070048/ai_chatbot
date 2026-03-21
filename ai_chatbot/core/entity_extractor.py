# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Entity Extractor for AI Chatbot Tool Router

Extracts structured entities from user messages using regex patterns.
No Frappe/DB dependencies — pure Python module for deterministic extraction.

Extracted entities:
- ISO dates (YYYY-MM-DD)
- Relative date references ("last month", "this quarter", "FY 2025")
- @mention references (company, customer, item)
- Document references (INV-2026-00001, SO-00123, etc.)
"""

from __future__ import annotations

import re

# ── Date patterns ────────────────────────────────────────────────────

DATE_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

DATE_RELATIVE = re.compile(
	r"\b("
	r"today|yesterday|"
	r"last (?:week|month|quarter|year)|"
	r"this (?:week|month|quarter|year|fy)|"
	r"previous (?:month|quarter|year)|"
	r"next (?:month|quarter|year)|"
	r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
	r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
	r"(?: \d{4})?|"
	r"q[1-4](?: \d{4})?|"
	r"fy ?\d{4}(?:[/-]\d{2,4})?"
	r")\b",
	re.IGNORECASE,
)

# ── @mention patterns (from the chat input's mention system) ─────────

MENTION_COMPANY = re.compile(r"@company:(\S+)")
MENTION_CUSTOMER = re.compile(r"@customer:(\S+)")
MENTION_ITEM = re.compile(r"@item:(\S+)")
MENTION_PERIOD = re.compile(r"@period:(\S+)")

# ── Document reference patterns ─────────────────────────────────────

DOC_REF = re.compile(
	r"\b("
	r"(?:ACC-[A-Z]+-\d{4}-\d+)|"
	r"(?:(?:INV|SINV|PINV|SO|PO|QTN|DN|PR|PE|JV|"
	r"LEAD|OPP|CRM|HR|EMP|SAL|ATT|TODO|MAT)-"
	r"[\w-]+)"
	r")\b",
	re.IGNORECASE,
)


def extract_entities(user_message: str) -> dict:
	"""Extract entities from a user message using regex patterns.

	Args:
		user_message: The raw user message text.

	Returns:
		Dict with entity keys and their extracted values.
		Keys present only when entities are found:
		- dates: list of ISO date strings
		- date_references: list of relative date strings
		- companies: list of @company mention values
		- customers: list of @customer mention values
		- items: list of @item mention values
		- periods: list of @period mention values
		- doc_refs: list of document reference strings
	"""
	entities: dict = {}

	# ISO dates
	iso_dates = DATE_ISO.findall(user_message)
	if iso_dates:
		entities["dates"] = iso_dates

	# Relative date references
	rel_dates = DATE_RELATIVE.findall(user_message)
	if rel_dates:
		entities["date_references"] = [d.strip() for d in rel_dates]

	# @mentions
	companies = MENTION_COMPANY.findall(user_message)
	if companies:
		entities["companies"] = companies

	customers = MENTION_CUSTOMER.findall(user_message)
	if customers:
		entities["customers"] = customers

	items = MENTION_ITEM.findall(user_message)
	if items:
		entities["items"] = items

	periods = MENTION_PERIOD.findall(user_message)
	if periods:
		entities["periods"] = periods

	# Document references
	doc_refs = DOC_REF.findall(user_message)
	if doc_refs:
		entities["doc_refs"] = doc_refs

	return entities
