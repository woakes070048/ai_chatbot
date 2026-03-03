# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Multi-Currency Utilities for AI Chatbot

Provides currency conversion and formatting using ERPNext's
Currency Exchange doctype and company currency settings.
"""

import frappe
from frappe.utils import flt, fmt_money, nowdate

from ai_chatbot.core.config import get_company_currency, get_default_company
from ai_chatbot.core.constants import BASE_AMOUNT_FIELDS


def get_exchange_rate(from_currency, to_currency, date=None):
	"""Get exchange rate between two currencies.

	Uses ERPNext's Currency Exchange doctype for rates. Falls back to 1.0
	if currencies are the same.

	Args:
		from_currency: Source currency code (e.g. "EUR").
		to_currency: Target currency code (e.g. "USD").
		date: Date for the exchange rate. Defaults to today.

	Returns:
		float — exchange rate.
	"""
	if from_currency == to_currency:
		return 1.0

	date = date or nowdate()

	# Try ERPNext's built-in method first
	try:
		from erpnext.setup.utils import get_exchange_rate as erp_get_exchange_rate

		rate = erp_get_exchange_rate(from_currency, to_currency, date)
		if rate:
			return flt(rate)
	except (ImportError, Exception):
		pass

	# Fallback: check Currency Exchange doctype directly
	rate = frappe.db.get_value(
		"Currency Exchange",
		{
			"from_currency": from_currency,
			"to_currency": to_currency,
			"date": ["<=", date],
		},
		"exchange_rate",
		order_by="date desc",
	)

	return flt(rate) or 1.0


def convert_to_company_currency(amount, from_currency, company=None, date=None):
	"""Convert an amount from a foreign currency to the company's base currency.

	Args:
		amount: The amount to convert.
		from_currency: Source currency code.
		company: Company name. Auto-resolved if not provided.
		date: Date for the exchange rate.

	Returns:
		float — converted amount in company currency.
	"""
	company = get_default_company(company)
	company_currency = get_company_currency(company)

	if from_currency == company_currency:
		return flt(amount)

	rate = get_exchange_rate(from_currency, company_currency, date)
	return flt(amount) * flt(rate)


def get_base_amount_field(doctype):
	"""Get the base (company currency) amount field name for a doctype.

	Use this field when aggregating monetary values to ensure
	all amounts are in the same company currency.

	Args:
		doctype: Frappe doctype name.

	Returns:
		str — field name (e.g. "base_grand_total").
	"""
	return BASE_AMOUNT_FIELDS.get(doctype, "base_grand_total")


def format_currency(amount, currency=None, company=None):
	"""Format an amount with currency symbol.

	Args:
		amount: Numeric amount.
		currency: Currency code. If not provided, uses company currency.
		company: Company name for resolving currency.

	Returns:
		str — formatted amount (e.g. "$1,234.56").
	"""
	if not currency and company:
		currency = get_company_currency(company)
	elif not currency:
		currency = frappe.defaults.get_global_default("currency") or "USD"

	return fmt_money(flt(amount), currency=currency)


def _add_company_label(data, company):
	"""Add company_label with subsidiary notation to a response dict."""
	conversation_id = getattr(frappe.flags, "current_conversation_id", None)
	if conversation_id:
		try:
			from ai_chatbot.core.session_context import build_company_label

			data["company_label"] = build_company_label(company, conversation_id)
		except Exception:
			data["company_label"] = company
	else:
		data["company_label"] = company


def build_company_context(data, company):
	"""Add company and company_label to a non-monetary tool response.

	For tools that return counts/non-monetary data but should still include
	company context with subsidiary notation.

	Args:
		data: Dict of tool response data.
		company: Company name.

	Returns:
		Dict with company and company_label fields added.
	"""
	data["company"] = company
	_add_company_label(data, company)
	return data


def build_currency_response(data, company):
	"""Add standard currency and company fields to a tool response dict.

	Every monetary tool response should call this to ensure consistent
	multi-company/multi-currency metadata. Includes subsidiary notation
	and session-level target currency if set.

	Args:
		data: Dict of tool response data.
		company: Company name.

	Returns:
		Dict with company, company_label, and currency fields added.
	"""
	data["company"] = company
	data["currency"] = get_company_currency(company)

	_add_company_label(data, company)

	# Override currency if target_currency is set in session
	conversation_id = getattr(frappe.flags, "current_conversation_id", None)
	if conversation_id:
		try:
			from ai_chatbot.core.session_context import get_session_context

			ctx = get_session_context(conversation_id)
			if ctx.get("target_currency"):
				data["currency"] = ctx["target_currency"]
		except Exception:
			pass

	return data
