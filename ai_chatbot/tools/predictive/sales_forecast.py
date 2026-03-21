# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Revenue Forecasting Tools

Projects future revenue based on historical Sales Invoice data.
Includes company-level revenue forecast and per-territory breakdown.
"""

import frappe
from frappe.query_builder import functions as fn
from frappe.utils import add_months, flt, get_first_day, get_last_day, nowdate

from ai_chatbot.core.constants import MAX_FORECAST_MONTHS, MIN_FORECAST_HISTORY
from ai_chatbot.core.exceptions import InsufficientDataError
from ai_chatbot.core.session_context import get_company_filter
from ai_chatbot.data.charts import build_multi_series_chart
from ai_chatbot.data.currency import build_currency_response
from ai_chatbot.data.forecast_charts import build_forecast_chart
from ai_chatbot.data.forecasting import fill_month_gaps, forecast_time_series, generate_month_labels
from ai_chatbot.tools.common import apply_company_filter as _apply_company_filter
from ai_chatbot.tools.common import primary as _primary
from ai_chatbot.tools.registry import register_tool


def _get_monthly_revenue(company, months_back: int = 24) -> tuple[list[str], list[float]]:
	"""Query monthly revenue from Sales Invoice (base_grand_total).

	Returns:
		(labels, values) — e.g. (["2025-01", "2025-02"], [50000.0, 62000.0])
	"""
	si = frappe.qb.DocType("Sales Invoice")
	start_date = get_first_day(add_months(nowdate(), -months_back + 1))
	end_date = get_last_day(nowdate())
	month_expr = fn.DateFormat(si.posting_date, "%Y-%m")

	query = (
		frappe.qb.from_(si)
		.select(
			month_expr.as_("month"),
			fn.Sum(si.base_grand_total).as_("total"),
		)
		.where(si.docstatus == 1)
		.where(si.posting_date >= start_date)
		.where(si.posting_date <= end_date)
	)
	query = _apply_company_filter(query, si, company)
	rows = query.groupby(month_expr).orderby(month_expr).run(as_dict=True)

	start_month = (
		f"{start_date.year:04d}-{start_date.month:02d}"
		if hasattr(start_date, "year")
		else str(start_date)[:7]
	)
	return fill_month_gaps(rows, "month", "total", start_month, months_back)


def _get_territory_monthly_revenue(
	territory: str, company, months_back: int = 24
) -> tuple[list[str], list[float]]:
	"""Query monthly revenue for a specific territory."""
	si = frappe.qb.DocType("Sales Invoice")
	start_date = get_first_day(add_months(nowdate(), -months_back + 1))
	end_date = get_last_day(nowdate())
	month_expr = fn.DateFormat(si.posting_date, "%Y-%m")

	query = (
		frappe.qb.from_(si)
		.select(
			month_expr.as_("month"),
			fn.Sum(si.base_grand_total).as_("total"),
		)
		.where(si.docstatus == 1)
		.where(si.territory == territory)
		.where(si.posting_date >= start_date)
		.where(si.posting_date <= end_date)
	)
	query = _apply_company_filter(query, si, company)
	rows = query.groupby(month_expr).orderby(month_expr).run(as_dict=True)

	start_month = (
		f"{start_date.year:04d}-{start_date.month:02d}"
		if hasattr(start_date, "year")
		else str(start_date)[:7]
	)
	return fill_month_gaps(rows, "month", "total", start_month, months_back)


@register_tool(
	name="forecast_revenue",
	category="predictive",
	description=(
		"Forecast future revenue based on historical sales invoice data. "
		"Returns predicted monthly revenue with confidence intervals and a chart. "
		"Uses statistical methods (moving average, exponential smoothing, trend analysis)."
	),
	parameters={
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
def forecast_revenue(months_ahead=3, company=None):
	"""Forecast revenue using statistical time-series methods."""
	company = get_company_filter(company)
	months_ahead = min(max(1, months_ahead or 3), MAX_FORECAST_MONTHS)

	labels, values = _get_monthly_revenue(company)

	# Trim leading zeros
	first_nonzero = next((i for i, v in enumerate(values) if v > 0), len(values))
	labels = labels[first_nonzero:]
	values = values[first_nonzero:]

	if len(values) < MIN_FORECAST_HISTORY:
		return {
			"error": (
				f"Insufficient historical revenue data. "
				f"Need at least {MIN_FORECAST_HISTORY} months, found {len(values)}."
			),
			"historical_months": len(values),
		}

	try:
		result = forecast_time_series(values, months_ahead=months_ahead)
	except InsufficientDataError:
		return {
			"error": "Not enough data to forecast revenue.",
			"historical_months": len(values),
		}

	forecast_labels = generate_month_labels(labels[-1], months_ahead)

	echart = build_forecast_chart(
		title="Revenue Forecast",
		historical_labels=labels[-12:],
		historical_values=values[-12:],
		forecast_labels=forecast_labels,
		forecast_values=result["forecast"],
		confidence_95=result["confidence_95"],
		y_axis_name="Revenue",
	)

	forecast_data = []
	for i, month in enumerate(forecast_labels):
		forecast_data.append(
			{
				"month": month,
				"predicted_revenue": flt(result["forecast"][i], 2),
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
		"historical_months": len(values),
		"forecast_months": months_ahead,
		"method": result["method_used"],
		"trend": result["trend"],
		"seasonality_detected": result["seasonality_detected"],
		"total_historical_revenue": flt(sum(values), 2),
		"average_monthly_revenue": flt(result["historical_mean"], 2),
		"forecast": forecast_data,
		"total_forecasted_revenue": flt(sum(result["forecast"]), 2),
		"echart_option": echart,
	}
	return build_currency_response(data, _primary(company))


@register_tool(
	name="forecast_by_territory",
	category="predictive",
	description=(
		"Forecast revenue by territory/region based on historical sales data. "
		"Runs separate forecasts for top territories and shows a comparison chart."
	),
	parameters={
		"months_ahead": {
			"type": "integer",
			"description": "Number of months to forecast (default 3, max 6)",
		},
		"company": {
			"type": "string",
			"description": "Company name. Optional — omit to use user's default company.",
		},
	},
	doctypes=["Sales Invoice"],
)
def forecast_by_territory(months_ahead=3, company=None):
	"""Forecast revenue per territory using statistical methods."""
	company = get_company_filter(company)
	months_ahead = min(max(1, months_ahead or 3), 6)

	# Get top 5 territories by historical revenue
	si = frappe.qb.DocType("Sales Invoice")
	start_date = get_first_day(add_months(nowdate(), -23))

	territory_query = (
		frappe.qb.from_(si)
		.select(
			si.territory,
			fn.Sum(si.base_grand_total).as_("total"),
		)
		.where(si.docstatus == 1)
		.where(si.territory.isnotnull())
		.where(si.territory != "")
		.where(si.posting_date >= start_date)
	)
	territory_query = _apply_company_filter(territory_query, si, company)
	top_territories = (
		territory_query.groupby(si.territory)
		.orderby(fn.Sum(si.base_grand_total), order=frappe.qb.desc)
		.limit(5)
		.run(as_dict=True)
	)

	if not top_territories:
		return {"error": "No territory data found in Sales Invoices."}

	# Forecast each territory
	territory_forecasts = []
	chart_series = []
	forecast_labels = None

	for t in top_territories:
		territory_name = t.territory
		labels, values = _get_territory_monthly_revenue(territory_name, company)

		# Trim leading zeros
		first_nonzero = next((i for i, v in enumerate(values) if v > 0), len(values))
		labels = labels[first_nonzero:]
		values = values[first_nonzero:]

		if len(values) < MIN_FORECAST_HISTORY:
			territory_forecasts.append(
				{
					"territory": territory_name,
					"historical_revenue": flt(t.total, 2),
					"status": "insufficient_data",
					"historical_months": len(values),
				}
			)
			continue

		try:
			result = forecast_time_series(values, months_ahead=months_ahead)
		except InsufficientDataError:
			territory_forecasts.append(
				{
					"territory": territory_name,
					"historical_revenue": flt(t.total, 2),
					"status": "insufficient_data",
					"historical_months": len(values),
				}
			)
			continue

		if forecast_labels is None:
			forecast_labels = generate_month_labels(labels[-1], months_ahead)

		territory_forecasts.append(
			{
				"territory": territory_name,
				"historical_revenue": flt(t.total, 2),
				"status": "forecasted",
				"trend": result["trend"],
				"method": result["method_used"],
				"forecast": [
					{"month": m, "predicted_revenue": flt(v, 2)}
					for m, v in zip(forecast_labels, result["forecast"], strict=True)
				],
				"total_forecasted": flt(sum(result["forecast"]), 2),
			}
		)

		# Add to chart series
		chart_series.append(
			{
				"name": territory_name,
				"data": [flt(v, 2) for v in result["forecast"]],
			}
		)

	# Build comparison chart
	echart = None
	if forecast_labels and chart_series:
		echart = build_multi_series_chart(
			title="Revenue Forecast by Territory",
			categories=forecast_labels,
			series_list=chart_series,
			y_axis_name="Revenue",
			chart_type="bar",
		)

	data = {
		"forecast_months": months_ahead,
		"territories": territory_forecasts,
		"echart_option": echart,
	}
	return build_currency_response(data, _primary(company))
