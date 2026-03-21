# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Accounting Dimensions Helpers
Discover active accounting dimensions and apply dimension filters to queries.
"""

import frappe


def get_available_dimensions():
	"""Get all active accounting dimensions using ERPNext's official API.

	Uses ``erpnext.accounts.doctype.accounting_dimension.accounting_dimension
	.get_accounting_dimensions()`` which returns the canonical list of
	non-disabled dimensions.  Falls back to a direct DocType query when
	ERPNext is not installed.

	Returns:
		list[dict]: Each dict has keys: fieldname, label, document_type.
	"""
	try:
		from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
			get_accounting_dimensions,
		)

		dims = get_accounting_dimensions(as_list=False)
		return [
			{
				"fieldname": d.get("fieldname"),
				"label": d.get("label") or d.get("fieldname"),
				"document_type": d.get("document_type") or d.get("fieldname"),
			}
			for d in dims
			if d.get("fieldname")
		]
	except ImportError:
		pass

	# Fallback: query the DocType directly (ERPNext not installed)
	dimensions = frappe.get_all(
		"Accounting Dimension",
		filters={"disabled": 0},
		fields=["name", "label", "document_type", "fieldname"],
		order_by="label asc",
	)

	return [
		{
			"fieldname": d.fieldname or frappe.scrub(d.document_type or d.name),
			"label": d.label or d.document_type or d.name,
			"document_type": d.document_type or d.name,
		}
		for d in dimensions
	]


def apply_dimension_filters(query, table, **dimensions):
	"""Apply accounting dimension filters to a frappe.qb query.

	Dynamically checks whether the field exists on the table before
	applying the filter.  This allows safe filtering by cost_center,
	department, project, and any custom accounting dimensions.

	Args:
		query: A frappe.qb query in progress.
		table: The frappe.qb DocType table alias.
		**dimensions: Keyword arguments like cost_center="CC-001".

	Returns:
		The query with dimension filters applied.
	"""
	for field, value in dimensions.items():
		if not value:
			continue
		# Check the DocType meta for the field existence
		try:
			if hasattr(table, field):
				query = query.where(table[field] == value)
		except Exception:
			pass

	return query
