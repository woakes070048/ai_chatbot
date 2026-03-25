# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Purchase Report Tools (Phase 12B)

Thin wrappers around ERPNext's standard purchase report execute() functions.

Reports covered:
1. Purchase Register
2. Item-wise Purchase Register
"""

from __future__ import annotations

from ai_chatbot.core.config import get_default_company, get_fiscal_year_dates
from ai_chatbot.tools.registry import register_tool
from ai_chatbot.tools.reports._base import build_report_response, run_report

# ═══════════════════════════════════════════════════════════════════
# 1. Purchase Register
# ═══════════════════════════════════════════════════════════════════


@register_tool(
	name="report_purchase_register",
	category="buying",
	description=(
		"Run ERPNext Purchase Register — shows all purchase transactions for a period "
		"with invoiced amount and tax details. Each tax type gets a separate column, "
		"making it easy to see total taxes paid for each tax type."
	),
	parameters={
		"company": {
			"type": "string",
			"description": "Company name. Optional — omit to use user's default company.",
		},
		"from_date": {
			"type": "string",
			"description": "Start date (YYYY-MM-DD). Optional — defaults to fiscal year start.",
		},
		"to_date": {
			"type": "string",
			"description": "End date (YYYY-MM-DD). Optional — defaults to fiscal year end.",
		},
		"supplier": {
			"type": "string",
			"description": "Filter by supplier name.",
		},
		"supplier_group": {
			"type": "string",
			"description": "Filter by supplier group.",
		},
	},
	doctypes=["Purchase Invoice"],
)
def report_purchase_register(
	company=None,
	from_date=None,
	to_date=None,
	supplier=None,
	supplier_group=None,
):
	"""Run ERPNext Purchase Register report."""
	company = get_default_company(company)

	if not from_date or not to_date:
		fy_from, fy_to = get_fiscal_year_dates(company)
		from_date = from_date or fy_from
		to_date = to_date or fy_to

	filters = {
		"company": company,
		"from_date": from_date,
		"to_date": to_date,
	}

	if supplier:
		filters["supplier"] = supplier
	if supplier_group:
		filters["supplier_group"] = supplier_group

	from erpnext.accounts.report.purchase_register.purchase_register import execute

	result = run_report(execute, filters)
	result["period"] = {"from": from_date, "to": to_date}
	return build_report_response(result, company)


# ═══════════════════════════════════════════════════════════════════
# 2. Item-wise Purchase Register
# ═══════════════════════════════════════════════════════════════════


@register_tool(
	name="report_item_wise_purchase_register",
	category="buying",
	description=(
		"Run ERPNext Item-wise Purchase Register — shows all purchase transactions "
		"for a period broken down by item with rate, quantity, amount, and tax details. "
		"Use to identify which items are purchased the most and their tax breakdown."
	),
	parameters={
		"company": {
			"type": "string",
			"description": "Company name. Optional — omit to use user's default company.",
		},
		"from_date": {
			"type": "string",
			"description": "Start date (YYYY-MM-DD). Optional — defaults to fiscal year start.",
		},
		"to_date": {
			"type": "string",
			"description": "End date (YYYY-MM-DD). Optional — defaults to fiscal year end.",
		},
		"supplier": {
			"type": "string",
			"description": "Filter by supplier name.",
		},
		"item_code": {
			"type": "string",
			"description": "Filter by specific item code.",
		},
		"item_group": {
			"type": "string",
			"description": "Filter by item group.",
		},
	},
	doctypes=["Purchase Invoice"],
)
def report_item_wise_purchase_register(
	company=None,
	from_date=None,
	to_date=None,
	supplier=None,
	item_code=None,
	item_group=None,
):
	"""Run ERPNext Item-wise Purchase Register report."""
	company = get_default_company(company)

	if not from_date or not to_date:
		fy_from, fy_to = get_fiscal_year_dates(company)
		from_date = from_date or fy_from
		to_date = to_date or fy_to

	filters = {
		"company": company,
		"from_date": from_date,
		"to_date": to_date,
	}

	if supplier:
		filters["supplier"] = supplier
	if item_code:
		filters["item_code"] = item_code
	if item_group:
		filters["item_group"] = item_group

	from erpnext.accounts.report.item_wise_purchase_register.item_wise_purchase_register import (
		execute,
	)

	result = run_report(execute, filters)
	result["period"] = {"from": from_date, "to": to_date}
	return build_report_response(result, company)
