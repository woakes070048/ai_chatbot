# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Trend Analysis Tool

Analyses historical trends in revenue, expenses, item demand, and
custom metrics. Returns comprehensive statistics including linear
regression, growth rates, moving averages, seasonality detection,
and a visual chart with trend line overlay.
"""

import frappe
from frappe.query_builder import functions as fn
from frappe.utils import add_months, flt, get_first_day, get_last_day, nowdate

from ai_chatbot.core.session_context import get_company_filter
from ai_chatbot.data.currency import build_currency_response
from ai_chatbot.data.forecast_charts import build_trend_analysis_chart
from ai_chatbot.data.forecasting import analyse_trend, fill_month_gaps, linear_regression
from ai_chatbot.tools.common import apply_company_filter as _apply_company_filter
from ai_chatbot.tools.common import primary as _primary
from ai_chatbot.tools.registry import register_tool


def _get_monthly_series(
	doctype: str,
	amount_field: str,
	company,
	months_back: int,
	item_code: str | None = None,
) -> tuple[list[str], list[float]]:
	"""Query monthly aggregated values for a doctype.

	Supports both header-level (Sales Invoice) and item-level
	(Sales Invoice Item) queries when item_code is provided.

	Returns:
		(labels, values) — zero-filled monthly time series.
	"""
	start_date = get_first_day(add_months(nowdate(), -months_back + 1))
	end_date = get_last_day(nowdate())

	if item_code and doctype in ("Sales Invoice", "Purchase Invoice"):
		# Item-level query via child table
		parent_dt = frappe.qb.DocType(doctype)
		child_dt = frappe.qb.DocType(f"{doctype} Item")
		month_expr = fn.DateFormat(parent_dt.posting_date, "%Y-%m")

		query = (
			frappe.qb.from_(child_dt)
			.join(parent_dt)
			.on(child_dt.parent == parent_dt.name)
			.select(
				month_expr.as_("month"),
				fn.Sum(child_dt.stock_qty).as_("total"),
			)
			.where(parent_dt.docstatus == 1)
			.where(child_dt.item_code == item_code)
			.where(parent_dt.posting_date >= start_date)
			.where(parent_dt.posting_date <= end_date)
		)
		query = _apply_company_filter(query, parent_dt, company)
	else:
		# Header-level query
		table = frappe.qb.DocType(doctype)
		month_expr = fn.DateFormat(table.posting_date, "%Y-%m")

		query = (
			frappe.qb.from_(table)
			.select(
				month_expr.as_("month"),
				fn.Sum(table[amount_field]).as_("total"),
			)
			.where(table.docstatus == 1)
			.where(table.posting_date >= start_date)
			.where(table.posting_date <= end_date)
		)
		query = _apply_company_filter(query, table, company)

	rows = query.groupby(month_expr).orderby(month_expr).run(as_dict=True)

	start_month = (
		f"{start_date.year:04d}-{start_date.month:02d}"
		if hasattr(start_date, "year")
		else str(start_date)[:7]
	)
	return fill_month_gaps(rows, "month", "total", start_month, months_back)


@register_tool(
	name="analyse_trend",
	category="predictive",
	description=(
		"Analyse historical trends in revenue, expenses, or item demand over time. "
		"Returns linear regression, growth rates, moving averages, seasonality detection, "
		"and a chart with trend line overlay. "
		"Use metric='revenue' for sales, 'expenses' for purchases, 'demand' for item quantity."
	),
	parameters={
		"metric": {
			"type": "string",
			"description": (
				"What to analyse: 'revenue' (Sales Invoice totals), "
				"'expenses' (Purchase Invoice totals), "
				"'demand' (item sold quantity — requires item_code). "
				"Default: 'revenue'"
			),
		},
		"months": {
			"type": "integer",
			"description": "Number of months of history to analyse (default 12, max 36)",
		},
		"item_code": {
			"type": "string",
			"description": "Item code for demand trend analysis (only used when metric='demand')",
		},
		"company": {
			"type": "string",
			"description": "Company name. Optional — omit to use user's default company.",
		},
	},
	doctypes=["Sales Invoice", "Purchase Invoice"],
)
def analyse_trend_tool(metric="revenue", months=12, item_code=None, company=None):
	"""Analyse historical trends using linear regression and statistical methods."""
	company = get_company_filter(company)
	months = min(max(3, months or 12), 36)

	metric_config = {
		"revenue": {
			"doctype": "Sales Invoice",
			"amount_field": "base_grand_total",
			"label": "Revenue",
			"chart_title": "Revenue Trend Analysis",
			"y_axis": "Revenue",
		},
		"expenses": {
			"doctype": "Purchase Invoice",
			"amount_field": "base_grand_total",
			"label": "Expenses",
			"chart_title": "Expense Trend Analysis",
			"y_axis": "Expenses",
		},
		"demand": {
			"doctype": "Sales Invoice",
			"amount_field": "stock_qty",
			"label": "Demand (Qty)",
			"chart_title": "Demand Trend Analysis",
			"y_axis": "Quantity",
		},
	}

	if metric not in metric_config:
		return {"error": f"Invalid metric '{metric}'. Use 'revenue', 'expenses', or 'demand'."}

	config = metric_config[metric]

	if metric == "demand" and not item_code:
		return {"error": "item_code is required for demand trend analysis."}

	# Resolve item if needed
	if metric == "demand":
		resolved = _resolve_item(item_code)
		if not resolved:
			return {"error": f"Item '{item_code}' not found."}
		item_code = resolved

	labels, values = _get_monthly_series(
		doctype=config["doctype"],
		amount_field=config["amount_field"],
		company=company,
		months_back=months,
		item_code=item_code if metric == "demand" else None,
	)

	# Trim leading zeros
	first_nonzero = next((i for i, v in enumerate(values) if v > 0), len(values))
	labels = labels[first_nonzero:]
	values = values[first_nonzero:]

	if len(values) < 2:
		return {
			"error": f"Insufficient data for trend analysis. Found {len(values)} data points.",
			"metric": metric,
		}

	# Run trend analysis
	analysis = analyse_trend(values, labels)

	# Build regression line for chart
	n = len(values)
	slope, intercept = linear_regression(values)
	trend_line = [slope * i + intercept for i in range(n)]

	# Build chart
	echart = build_trend_analysis_chart(
		title=config["chart_title"],
		labels=labels,
		values=values,
		trend_line=trend_line,
		ma3=analysis.get("moving_average_3", []),
		ma6=analysis.get("moving_average_6", []),
		y_axis_name=config["y_axis"],
	)

	# Build response
	data = {
		"metric": metric,
		"period_months": len(values),
		"analysis": {
			"trend": analysis["trend"],
			"slope_per_month": analysis["slope_per_period"],
			"r_squared": analysis["r_squared"],
			"total_change_pct": analysis["total_change_pct"],
			"average_growth_pct": analysis["average_growth_pct"],
			"first_half_mean": analysis["first_half_mean"],
			"second_half_mean": analysis["second_half_mean"],
			"half_change_pct": analysis["half_change_pct"],
			"seasonality_detected": analysis["seasonality_detected"],
		},
		"summary_stats": {
			"mean": analysis["mean"],
			"std_dev": analysis["std_dev"],
			"min": analysis["min"],
			"max": analysis["max"],
			"first_value": analysis["first_value"],
			"last_value": analysis["last_value"],
		},
		"growth_rates": analysis["growth_rates"],
		"echart_option": echart,
	}

	if metric == "demand":
		item_name = frappe.db.get_value("Item", item_code, "item_name") or item_code
		data["item_code"] = item_code
		data["item_name"] = item_name
		# Demand is non-monetary — use company context without currency
		from ai_chatbot.data.currency import build_company_context

		return build_company_context(data, _primary(company))

	return build_currency_response(data, _primary(company))


def _resolve_item(item_code: str) -> str | None:
	"""Resolve item_code by exact match, then fuzzy item_name match."""
	if frappe.db.exists("Item", item_code):
		return item_code

	resolved = frappe.db.get_value("Item", {"item_name": ["like", f"%{item_code}%"]}, "name")
	if resolved:
		return resolved

	resolved = frappe.db.get_value("Item", {"name": ["like", f"%{item_code}%"]}, "name")
	return resolved
