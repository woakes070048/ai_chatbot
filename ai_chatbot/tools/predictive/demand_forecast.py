# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Demand Forecasting Tool

Projects future item demand (quantity) based on historical Sales Invoice data.
Uses statistical time-series methods from the forecasting engine.
"""

import frappe
from frappe.query_builder import functions as fn
from frappe.utils import add_months, flt, get_first_day, get_last_day, nowdate

from ai_chatbot.core.constants import MAX_FORECAST_MONTHS, MIN_FORECAST_HISTORY
from ai_chatbot.core.exceptions import InsufficientDataError
from ai_chatbot.core.session_context import get_company_filter
from ai_chatbot.data.currency import build_company_context
from ai_chatbot.data.forecast_charts import build_forecast_chart
from ai_chatbot.data.forecasting import fill_month_gaps, forecast_time_series, generate_month_labels
from ai_chatbot.tools.registry import register_tool


def _primary(company):
	return company[0] if isinstance(company, list) else company


def _apply_company_filter(query, table, company):
	if isinstance(company, list):
		return query.where(table.company.isin(company))
	return query.where(table.company == company)


def _get_monthly_demand(item_code: str, company, months_back: int = 24) -> tuple[list[str], list[float]]:
	"""Query monthly sold quantity for an item from Sales Invoice Item.

	Returns:
		(labels, values) — e.g. (["2025-01", "2025-02", ...], [100.0, 150.0, ...])
	"""
	si = frappe.qb.DocType("Sales Invoice")
	sii = frappe.qb.DocType("Sales Invoice Item")
	start_date = get_first_day(add_months(nowdate(), -months_back + 1))
	end_date = get_last_day(nowdate())
	month_expr = fn.DateFormat(si.posting_date, "%Y-%m")

	query = (
		frappe.qb.from_(sii)
		.join(si)
		.on(sii.parent == si.name)
		.select(
			month_expr.as_("month"),
			fn.Sum(sii.stock_qty).as_("total_qty"),
		)
		.where(si.docstatus == 1)
		.where(sii.item_code == item_code)
		.where(si.posting_date >= start_date)
		.where(si.posting_date <= end_date)
	)
	query = _apply_company_filter(query, si, company)
	rows = query.groupby(month_expr).orderby(month_expr).run(as_dict=True)

	# Fill gaps with zeros for continuous time series
	start_month = (
		f"{start_date.year:04d}-{start_date.month:02d}"
		if hasattr(start_date, "year")
		else str(start_date)[:7]
	)
	return fill_month_gaps(rows, "month", "total_qty", start_month, months_back)


def _resolve_item(item_code: str) -> str | None:
	"""Resolve item_code by exact match, then fuzzy item_name match.

	Returns the resolved item_code or None if not found.
	"""
	if frappe.db.exists("Item", item_code):
		return item_code

	# Try fuzzy match on item_name
	resolved = frappe.db.get_value("Item", {"item_name": ["like", f"%{item_code}%"]}, "name")
	if resolved:
		return resolved

	# Try fuzzy match on item_code
	resolved = frappe.db.get_value("Item", {"name": ["like", f"%{item_code}%"]}, "name")
	return resolved


@register_tool(
	name="forecast_demand",
	category="predictive",
	description=(
		"Forecast future demand (quantity) for a specific item based on historical sales. "
		"Returns predicted monthly quantities with confidence intervals and a chart. "
		"Uses statistical methods (moving average, exponential smoothing, trend analysis)."
	),
	parameters={
		"item_code": {
			"type": "string",
			"description": "Item code or item name to forecast demand for (required)",
		},
		"months_ahead": {
			"type": "integer",
			"description": "Number of months to forecast (default 3, max 12)",
		},
		"company": {
			"type": "string",
			"description": "Company name. Optional — omit to use user's default company.",
		},
	},
	doctypes=["Sales Invoice"],
)
def forecast_demand(item_code=None, months_ahead=3, company=None):
	"""Forecast item demand using statistical time-series methods."""
	if not item_code:
		return {"error": "item_code is required"}

	company = get_company_filter(company)
	months_ahead = min(max(1, months_ahead or 3), MAX_FORECAST_MONTHS)

	# Resolve item
	resolved = _resolve_item(item_code)
	if not resolved:
		return {"error": f"Item '{item_code}' not found"}
	item_code = resolved

	item_name = frappe.db.get_value("Item", item_code, "item_name") or item_code

	# Get historical demand data
	labels, values = _get_monthly_demand(item_code, company)

	# Trim leading zeros to find the actual start of sales
	first_nonzero = next((i for i, v in enumerate(values) if v > 0), len(values))
	labels = labels[first_nonzero:]
	values = values[first_nonzero:]

	if len(values) < MIN_FORECAST_HISTORY:
		return {
			"error": (
				f"Insufficient historical data for '{item_name}'. "
				f"Need at least {MIN_FORECAST_HISTORY} months with sales data, "
				f"found {len(values)}."
			),
			"item_code": item_code,
			"item_name": item_name,
			"historical_months": len(values),
		}

	# Run forecast
	try:
		result = forecast_time_series(values, months_ahead=months_ahead)
	except InsufficientDataError:
		return {
			"error": f"Not enough data to forecast demand for '{item_name}'.",
			"item_code": item_code,
			"historical_months": len(values),
		}

	# Build forecast month labels
	forecast_labels = generate_month_labels(labels[-1], months_ahead)

	# Build ECharts forecast chart
	echart = build_forecast_chart(
		title=f"Demand Forecast — {item_name}",
		historical_labels=labels[-12:],  # Show last 12 months of history
		historical_values=values[-12:],
		forecast_labels=forecast_labels,
		forecast_values=result["forecast"],
		confidence_95=result["confidence_95"],
		y_axis_name="Quantity",
	)

	# Build response
	forecast_data = []
	for i, month in enumerate(forecast_labels):
		forecast_data.append(
			{
				"month": month,
				"predicted_qty": flt(result["forecast"][i], 2),
				"confidence_80": {
					"low": flt(result["confidence_80"][i][0], 2),
					"high": flt(result["confidence_80"][i][1], 2),
				},
				"confidence_95": {
					"low": flt(result["confidence_95"][i][0], 2),
					"high": flt(result["confidence_95"][i][1], 2),
				},
			}
		)

	data = {
		"item_code": item_code,
		"item_name": item_name,
		"historical_months": len(values),
		"forecast_months": months_ahead,
		"method": result["method_used"],
		"trend": result["trend"],
		"seasonality_detected": result["seasonality_detected"],
		"average_monthly_demand": flt(result["historical_mean"], 2),
		"forecast": forecast_data,
		"echart_option": echart,
	}
	return build_company_context(data, _primary(company))
