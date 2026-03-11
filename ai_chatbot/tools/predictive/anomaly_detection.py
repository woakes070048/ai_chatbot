# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Anomaly Detection Tool

Identifies unusual transactions and patterns in financial data using
statistical methods (z-score, IQR). No ML dependencies required.

Detection covers:
- Unusually large amounts in Sales Invoice, Purchase Invoice, Payment Entry
- New suppliers/customers with large first orders
"""

import frappe
from frappe.query_builder import functions as fn
from frappe.utils import flt, getdate

from ai_chatbot.core.config import get_fiscal_year_dates
from ai_chatbot.core.session_context import get_company_filter
from ai_chatbot.data.charts import build_bar_chart
from ai_chatbot.data.currency import build_currency_response
from ai_chatbot.data.forecasting import _mean, _std
from ai_chatbot.tools.registry import register_tool


def _primary(company):
	return company[0] if isinstance(company, list) else company


def _apply_company_filter(query, table, company):
	if isinstance(company, list):
		return query.where(table.company.isin(company))
	return query.where(table.company == company)


@register_tool(
	name="detect_anomalies",
	category="predictive",
	description=(
		"Detect unusual transactions and patterns in financial data. "
		"Flags unusually large amounts, and new suppliers/customers with big first orders. "
		"Uses statistical methods (z-score and IQR) — configurable sensitivity."
	),
	parameters={
		"from_date": {
			"type": "string",
			"description": "Start date for analysis (YYYY-MM-DD). Optional — defaults to current fiscal year start.",
		},
		"to_date": {
			"type": "string",
			"description": "End date for analysis (YYYY-MM-DD). Optional — defaults to today.",
		},
		"sensitivity": {
			"type": "string",
			"description": "Detection sensitivity: 'low' (z>3.0), 'medium' (z>2.5, default), 'high' (z>2.0)",
		},
		"company": {
			"type": "string",
			"description": "Company name. Optional — omit to use user's default company.",
		},
	},
	doctypes=["Sales Invoice", "Purchase Invoice", "Payment Entry"],
)
def detect_anomalies(from_date=None, to_date=None, sensitivity="medium", company=None):
	"""Detect anomalies across sales, purchases, and payments."""
	company = get_company_filter(company)

	if not from_date or not to_date:
		fy_from, fy_to = get_fiscal_year_dates(_primary(company))
		from_date = from_date or fy_from
		to_date = to_date or fy_to

	# Map sensitivity to z-score threshold
	thresholds = {"low": 3.0, "medium": 2.5, "high": 2.0}
	z_threshold = thresholds.get(sensitivity, 2.5)

	anomalies = []

	# 1. Sales Invoice anomalies
	anomalies.extend(
		_detect_doctype_anomalies(
			doctype="Sales Invoice",
			amount_field="base_grand_total",
			date_field="posting_date",
			party_field="customer",
			party_label="Customer",
			from_date=from_date,
			to_date=to_date,
			company=company,
			z_threshold=z_threshold,
		)
	)

	# 2. Purchase Invoice anomalies
	anomalies.extend(
		_detect_doctype_anomalies(
			doctype="Purchase Invoice",
			amount_field="base_grand_total",
			date_field="posting_date",
			party_field="supplier",
			party_label="Supplier",
			from_date=from_date,
			to_date=to_date,
			company=company,
			z_threshold=z_threshold,
		)
	)

	# 3. Payment Entry anomalies
	anomalies.extend(
		_detect_doctype_anomalies(
			doctype="Payment Entry",
			amount_field="base_paid_amount",
			date_field="posting_date",
			party_field="party_name",
			party_label="Party",
			from_date=from_date,
			to_date=to_date,
			company=company,
			z_threshold=z_threshold,
		)
	)

	# 4. New party large orders
	anomalies.extend(
		_detect_new_party_large_orders(
			from_date=from_date,
			to_date=to_date,
			company=company,
			z_threshold=z_threshold,
		)
	)

	# Sort by severity (z-score descending)
	anomalies.sort(key=lambda x: abs(x.get("z_score", 0)), reverse=True)

	# Build summary by type
	type_counts: dict[str, int] = {}
	for a in anomalies:
		t = a.get("source_doctype", "Unknown")
		type_counts[t] = type_counts.get(t, 0) + 1

	chart_categories = list(type_counts.keys())
	chart_values = list(type_counts.values())

	echart = None
	if chart_categories:
		echart = build_bar_chart(
			title="Anomalies Detected by Type",
			categories=chart_categories,
			series_data=chart_values,
			y_axis_name="Count",
			series_name="Anomalies",
		)

	data = {
		"total_anomalies": len(anomalies),
		"anomalies": anomalies[:20],  # Limit to top 20
		"summary_by_type": type_counts,
		"sensitivity": sensitivity,
		"z_threshold": z_threshold,
		"period": {"from": from_date, "to": to_date},
		"echart_option": echart,
	}
	return build_currency_response(data, _primary(company))


def _detect_doctype_anomalies(
	doctype: str,
	amount_field: str,
	date_field: str,
	party_field: str,
	party_label: str,
	from_date: str,
	to_date: str,
	company,
	z_threshold: float,
) -> list[dict]:
	"""Detect amount anomalies in a specific doctype using z-score.

	Queries all submitted documents in the date range, computes z-scores
	for the amount field, and flags those exceeding the threshold.
	"""
	table = frappe.qb.DocType(doctype)

	query = (
		frappe.qb.from_(table)
		.select(
			table.name,
			table[amount_field].as_("amount"),
			table[date_field].as_("date"),
			table[party_field].as_("party"),
		)
		.where(table.docstatus == 1)
		.where(table[date_field] >= from_date)
		.where(table[date_field] <= to_date)
		.orderby(table[amount_field], order=frappe.qb.desc)
		.limit(5000)  # Safety limit for large datasets
	)
	query = _apply_company_filter(query, table, company)
	rows = query.run(as_dict=True)

	if len(rows) < 5:
		return []  # Not enough data for meaningful anomaly detection

	amounts = [flt(r.amount) for r in rows]
	mean = _mean(amounts)
	std = _std(amounts)

	if std < 1e-9:
		return []  # No variance — all amounts are the same

	anomalies = []
	for row in rows:
		amount = flt(row.amount)
		z = (amount - mean) / std

		if abs(z) > z_threshold:
			anomalies.append(
				{
					"source_doctype": doctype,
					"document_name": row.name,
					"date": str(row.date),
					"party_type": party_label,
					"party": row.party or "Unknown",
					"amount": flt(amount, 2),
					"z_score": round(z, 2),
					"reason": "unusually_large_amount" if z > 0 else "unusually_small_amount",
					"mean_amount": flt(mean, 2),
					"std_dev": flt(std, 2),
				}
			)

	return anomalies


def _detect_new_party_large_orders(
	from_date: str,
	to_date: str,
	company,
	z_threshold: float,
) -> list[dict]:
	"""Detect new suppliers/customers whose first transaction is unusually large.

	A "new" party is one whose first submitted Sales/Purchase Invoice falls
	within the analysis period. "Large" means the amount exceeds the
	overall average by z_threshold standard deviations.
	"""
	anomalies = []
	from_dt = getdate(from_date)

	# Check both Sales Invoice (customers) and Purchase Invoice (suppliers)
	checks = [
		("Sales Invoice", "customer", "Customer", "base_grand_total", "posting_date"),
		("Purchase Invoice", "supplier", "Supplier", "base_grand_total", "posting_date"),
	]

	for doctype, party_field, party_label, amount_field, date_field in checks:
		table = frappe.qb.DocType(doctype)

		# Get all parties with their first transaction date and amount
		first_txn_query = (
			frappe.qb.from_(table)
			.select(
				table[party_field].as_("party"),
				fn.Min(table[date_field]).as_("first_date"),
				fn.Min(table.name).as_("first_doc"),
			)
			.where(table.docstatus == 1)
			.where(table[party_field].isnotnull())
			.where(table[party_field] != "")
			.groupby(table[party_field])
		)
		first_txn_query = _apply_company_filter(first_txn_query, table, company)
		party_first = first_txn_query.run(as_dict=True)

		if not party_first:
			continue

		# Filter to parties whose first transaction is within analysis period
		new_parties = [p for p in party_first if getdate(p.first_date) >= from_dt]
		if not new_parties:
			continue

		# Get all transaction amounts for z-score computation
		all_amounts_query = (
			frappe.qb.from_(table)
			.select(fn.Avg(table[amount_field]).as_("avg_amount"))
			.where(table.docstatus == 1)
		)
		all_amounts_query = _apply_company_filter(all_amounts_query, table, company)
		avg_result = all_amounts_query.run(as_dict=True)
		overall_avg = flt(avg_result[0].avg_amount) if avg_result else 0

		if overall_avg < 1e-9:
			continue

		# Get standard deviation
		std_query = frappe.qb.from_(table).select(table[amount_field]).where(table.docstatus == 1).limit(5000)
		std_query = _apply_company_filter(std_query, table, company)
		all_rows = std_query.run(as_dict=True)
		all_amounts = [flt(r[amount_field]) for r in all_rows]
		overall_std = _std(all_amounts)

		if overall_std < 1e-9:
			continue

		# Check each new party's first order amount
		for party_info in new_parties:
			# Get the actual amount of their first transaction
			first_amount = frappe.db.get_value(
				doctype,
				{"name": party_info.first_doc},
				amount_field,
			)
			first_amount = flt(first_amount)

			z = (first_amount - overall_avg) / overall_std
			if z > z_threshold:
				anomalies.append(
					{
						"source_doctype": doctype,
						"document_name": party_info.first_doc,
						"date": str(party_info.first_date),
						"party_type": party_label,
						"party": party_info.party,
						"amount": flt(first_amount, 2),
						"z_score": round(z, 2),
						"reason": f"new_{party_label.lower()}_large_first_order",
						"mean_amount": flt(overall_avg, 2),
						"std_dev": flt(overall_std, 2),
					}
				)

	return anomalies
