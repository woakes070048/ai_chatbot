# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Common Tool Helpers
Shared utilities for all tool modules — eliminates duplication across files.
"""

from __future__ import annotations


def primary(company: str | list[str]) -> str:
	"""Get primary company name (first in list or string as-is)."""
	return company[0] if isinstance(company, list) else company


def apply_company_filter(query, doctype_ref, company: str | list[str]):
	"""Apply company filter supporting both single string and list.

	Args:
		query: A frappe.qb query object.
		doctype_ref: The DocType reference (e.g. `frappe.qb.DocType("Sales Invoice")`).
		company: Single company string or list of company strings.

	Returns:
		The query with the company filter applied.
	"""
	if isinstance(company, list):
		return query.where(doctype_ref.company.isin(company))
	return query.where(doctype_ref.company == company)
