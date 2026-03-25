# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
GL Entry-Based Finance Tools

Provides GL summary with flexible grouping by querying the General Ledger directly.

NOTE (Phase 12B): get_trial_balance and get_account_statement have been replaced by
report_trial_balance and report_general_ledger in tools/reports/finance.py which use
ERPNext's standard report functions for data consistency.
"""

import frappe
from frappe.query_builder import functions as fn
from frappe.utils import flt

from ai_chatbot.core.config import get_fiscal_year_dates
from ai_chatbot.core.session_context import get_company_filter
from ai_chatbot.data.charts import build_bar_chart, build_horizontal_bar
from ai_chatbot.data.currency import build_currency_response
from ai_chatbot.tools.finance.common import primary
from ai_chatbot.tools.registry import register_tool

# Maps group_by parameter values to their query fields
GROUP_BY_FIELDS = {
	"root_type": {"source": "account", "field": "root_type", "label": "Root Type"},
	"account_type": {"source": "account", "field": "account_type", "label": "Account Type"},
	"party_type": {"source": "gl_entry", "field": "party_type", "label": "Party Type"},
	"voucher_type": {"source": "gl_entry", "field": "voucher_type", "label": "Voucher Type"},
	"account_name": {"source": "gl_entry", "field": "account", "label": "Account"},
}

# Root types and their normal balance direction
# Asset/Expense: normal balance is debit (positive = debit - credit)
# Liability/Equity/Income: normal balance is credit (positive = credit - debit)
DEBIT_ROOT_TYPES = {"Asset", "Expense"}
CREDIT_ROOT_TYPES = {"Liability", "Equity", "Income"}


@register_tool(
	name="get_gl_summary",
	category="finance",
	description=(
		"Get General Ledger summary with flexible grouping by root type, account type, "
		"party type, voucher type, or account name. Uses GL entries for authoritative "
		"accounting data. Useful for cash & bank position, receivables, payables, and "
		"income/expense breakdowns."
	),
	parameters={
		"group_by": {
			"type": "string",
			"description": (
				"How to group the GL data. Options: 'root_type' (Asset/Liability/Equity/Income/Expense), "
				"'account_type' (Bank/Cash/Receivable/Payable/etc.), 'party_type' (Customer/Supplier/Employee), "
				"'voucher_type' (Sales Invoice/Purchase Invoice/etc.), 'account_name' (individual accounts). "
				"Default: 'root_type'"
			),
		},
		"root_type": {
			"type": "string",
			"description": "Filter by root type: 'Asset', 'Liability', 'Equity', 'Income', 'Expense'",
		},
		"account_type": {
			"type": "string",
			"description": "Filter by account type: 'Bank', 'Cash', 'Receivable', 'Payable', etc.",
		},
		"party_type": {
			"type": "string",
			"description": "Filter by party type: 'Customer', 'Supplier', 'Employee'",
		},
		"party": {
			"type": "string",
			"description": "Filter by specific party name",
		},
		"from_date": {
			"type": "string",
			"description": "Start date (YYYY-MM-DD). Optional — omit to use current fiscal year start.",
		},
		"to_date": {
			"type": "string",
			"description": "End date (YYYY-MM-DD). Optional — omit to use current fiscal year end.",
		},
		"company": {
			"type": "string",
			"description": "Company name. Optional — omit to use user's default company.",
		},
	},
	doctypes=["GL Entry", "Account"],
)
def get_gl_summary(
	group_by="root_type",
	root_type=None,
	account_type=None,
	party_type=None,
	party=None,
	from_date=None,
	to_date=None,
	company=None,
):
	"""Get GL summary grouped by the specified dimension."""
	company = get_company_filter(company)

	if not from_date or not to_date:
		fy_from, fy_to = get_fiscal_year_dates(primary(company))
		from_date = from_date or fy_from
		to_date = to_date or fy_to

	if group_by not in GROUP_BY_FIELDS:
		frappe.throw(f"Unsupported group_by: {group_by}. Options: {', '.join(GROUP_BY_FIELDS.keys())}")

	gle = frappe.qb.DocType("GL Entry")
	acc = frappe.qb.DocType("Account")

	group_config = GROUP_BY_FIELDS[group_by]
	if group_config["source"] == "account":
		group_col = acc[group_config["field"]]
	else:
		group_col = gle[group_config["field"]]

	query = (
		frappe.qb.from_(gle)
		.join(acc)
		.on(gle.account == acc.name)
		.select(
			group_col.as_("group_label"),
			fn.Sum(gle.debit).as_("total_debit"),
			fn.Sum(gle.credit).as_("total_credit"),
			(fn.Sum(gle.debit) - fn.Sum(gle.credit)).as_("balance"),
			fn.Count("*").as_("entry_count"),
		)
		.where(gle.is_cancelled == 0)
		.where(gle.posting_date >= from_date)
		.where(gle.posting_date <= to_date)
		.groupby(group_col)
		.orderby(fn.Sum(gle.debit) - fn.Sum(gle.credit), order=frappe.qb.desc)
	)

	if isinstance(company, list):
		query = query.where(gle.company.isin(company))
	else:
		query = query.where(gle.company == company)

	# Apply optional filters
	if root_type:
		query = query.where(acc.root_type == root_type)
	if account_type:
		query = query.where(acc.account_type == account_type)
	if party_type:
		query = query.where(gle.party_type == party_type)
	if party:
		query = query.where(gle.party == party)

	rows = query.run(as_dict=True)

	summary = []
	for row in rows:
		label = row.group_label or "Unknown"
		summary.append(
			{
				"label": label,
				"total_debit": flt(row.total_debit, 2),
				"total_credit": flt(row.total_credit, 2),
				"balance": flt(row.balance, 2),
				"entry_count": row.entry_count or 0,
			}
		)

	# Chart — use horizontal bar for account_name (long labels), bar chart otherwise
	categories = [s["label"] for s in summary[:15]]
	values = [abs(s["balance"]) for s in summary[:15]]

	if group_by == "account_name":
		chart = build_horizontal_bar(
			title=f"GL Summary by {group_config['label']}",
			categories=list(reversed(categories)),
			series_data=list(reversed(values)),
			x_axis_name="Balance",
			series_name="Balance",
		)
	else:
		chart = build_bar_chart(
			title=f"GL Summary by {group_config['label']}",
			categories=categories,
			series_data=values,
			y_axis_name="Balance",
			series_name="Balance",
		)

	totals = {
		"total_debit": flt(sum(s["total_debit"] for s in summary), 2),
		"total_credit": flt(sum(s["total_credit"] for s in summary), 2),
		"net_balance": flt(sum(s["balance"] for s in summary), 2),
	}

	result = {
		"group_by": group_by,
		"summary": summary,
		"totals": totals,
		"period": {"from": from_date, "to": to_date},
		"echart_option": chart,
	}
	return build_currency_response(result, primary(company))
