# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Cash Flow Forecasting Tool

Projects future cash inflows and outflows based on historical Payment Entry data.
Forecasts inflows (Receive) and outflows (Pay) separately, then computes net cash flow.
"""

import frappe
from frappe.query_builder import functions as fn
from frappe.utils import add_months, flt, get_first_day, get_last_day, nowdate

from ai_chatbot.core.constants import MAX_FORECAST_MONTHS, MIN_FORECAST_HISTORY
from ai_chatbot.core.exceptions import InsufficientDataError
from ai_chatbot.core.session_context import get_company_filter
from ai_chatbot.data.currency import build_currency_response
from ai_chatbot.data.forecast_charts import build_cash_flow_forecast_chart
from ai_chatbot.data.forecasting import fill_month_gaps, forecast_time_series, generate_month_labels
from ai_chatbot.tools.registry import register_tool


def _primary(company):
	return company[0] if isinstance(company, list) else company


def _apply_company_filter(query, table, company):
	if isinstance(company, list):
		return query.where(table.company.isin(company))
	return query.where(table.company == company)


def _get_monthly_cash_flow(company, months_back: int = 24) -> tuple[list[str], list[float], list[float]]:
	"""Query monthly inflows and outflows from Payment Entry.

	Returns:
		(labels, inflows, outflows) — parallel lists with zero-filled gaps.
	"""
	pe = frappe.qb.DocType("Payment Entry")
	start_date = get_first_day(add_months(nowdate(), -months_back + 1))
	end_date = get_last_day(nowdate())
	month_expr = fn.DateFormat(pe.posting_date, "%Y-%m")
	start_month = (
		f"{start_date.year:04d}-{start_date.month:02d}"
		if hasattr(start_date, "year")
		else str(start_date)[:7]
	)

	# Query inflows (Receive)
	inflow_q = (
		frappe.qb.from_(pe)
		.select(
			month_expr.as_("month"),
			fn.Sum(pe.base_paid_amount).as_("total"),
		)
		.where(pe.docstatus == 1)
		.where(pe.payment_type == "Receive")
		.where(pe.posting_date >= start_date)
		.where(pe.posting_date <= end_date)
	)
	inflow_q = _apply_company_filter(inflow_q, pe, company)
	inflow_rows = inflow_q.groupby(month_expr).orderby(month_expr).run(as_dict=True)

	# Query outflows (Pay)
	outflow_q = (
		frappe.qb.from_(pe)
		.select(
			month_expr.as_("month"),
			fn.Sum(pe.base_paid_amount).as_("total"),
		)
		.where(pe.docstatus == 1)
		.where(pe.payment_type == "Pay")
		.where(pe.posting_date >= start_date)
		.where(pe.posting_date <= end_date)
	)
	outflow_q = _apply_company_filter(outflow_q, pe, company)
	outflow_rows = outflow_q.groupby(month_expr).orderby(month_expr).run(as_dict=True)

	# Fill gaps for both series using the same month range
	labels, inflows = fill_month_gaps(inflow_rows, "month", "total", start_month, months_back)
	_, outflows = fill_month_gaps(outflow_rows, "month", "total", start_month, months_back)

	return labels, inflows, outflows


@register_tool(
	name="forecast_cash_flow",
	category="predictive",
	description=(
		"Forecast future cash flow (inflows and outflows) based on historical Payment Entry data. "
		"Returns projected monthly inflows, outflows, and net cash flow with a chart. "
		"Uses statistical methods to forecast inflows and outflows separately."
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
	doctypes=["Payment Entry"],
)
def forecast_cash_flow(months_ahead=3, company=None):
	"""Forecast cash flow — separate forecasts for inflow and outflow."""
	company = get_company_filter(company)
	months_ahead = min(max(1, months_ahead or 3), MAX_FORECAST_MONTHS)

	labels, inflows, outflows = _get_monthly_cash_flow(company)

	# Trim leading zeros (where both inflow and outflow are zero)
	first_nonzero = next(
		(i for i in range(len(labels)) if inflows[i] > 0 or outflows[i] > 0),
		len(labels),
	)
	labels = labels[first_nonzero:]
	inflows = inflows[first_nonzero:]
	outflows = outflows[first_nonzero:]

	if len(labels) < MIN_FORECAST_HISTORY:
		return {
			"error": (
				f"Insufficient payment history. "
				f"Need at least {MIN_FORECAST_HISTORY} months of data, found {len(labels)}."
			),
			"historical_months": len(labels),
		}

	# Forecast inflows and outflows separately
	try:
		inflow_result = forecast_time_series(inflows, months_ahead=months_ahead)
	except InsufficientDataError:
		return {"error": "Not enough inflow data to forecast.", "historical_months": len(labels)}

	try:
		outflow_result = forecast_time_series(outflows, months_ahead=months_ahead)
	except InsufficientDataError:
		return {"error": "Not enough outflow data to forecast.", "historical_months": len(labels)}

	# Compute net forecast
	net_forecast = [
		flt(i - o, 2) for i, o in zip(inflow_result["forecast"], outflow_result["forecast"], strict=True)
	]

	forecast_labels = generate_month_labels(labels[-1], months_ahead)

	# Build multi-series chart with historical + forecast for inflow/outflow/net
	echart = build_cash_flow_forecast_chart(
		historical_labels=labels[-12:],
		historical_inflows=inflows[-12:],
		historical_outflows=outflows[-12:],
		forecast_labels=forecast_labels,
		forecast_inflows=inflow_result["forecast"],
		forecast_outflows=outflow_result["forecast"],
	)

	# Build response
	forecast_data = []
	for i, month in enumerate(forecast_labels):
		forecast_data.append(
			{
				"month": month,
				"projected_inflow": flt(inflow_result["forecast"][i], 2),
				"projected_outflow": flt(outflow_result["forecast"][i], 2),
				"projected_net": flt(net_forecast[i], 2),
			}
		)

	# Historical summary
	hist_net = [flt(i - o, 2) for i, o in zip(inflows, outflows, strict=True)]

	data = {
		"historical_months": len(labels),
		"forecast_months": months_ahead,
		"inflow_method": inflow_result["method_used"],
		"outflow_method": outflow_result["method_used"],
		"inflow_trend": inflow_result["trend"],
		"outflow_trend": outflow_result["trend"],
		"average_monthly_inflow": flt(inflow_result["historical_mean"], 2),
		"average_monthly_outflow": flt(outflow_result["historical_mean"], 2),
		"average_monthly_net": flt(sum(hist_net) / len(hist_net) if hist_net else 0, 2),
		"forecast": forecast_data,
		"total_projected_inflow": flt(sum(inflow_result["forecast"]), 2),
		"total_projected_outflow": flt(sum(outflow_result["forecast"]), 2),
		"total_projected_net": flt(sum(net_forecast), 2),
		"echart_option": echart,
	}
	return build_currency_response(data, _primary(company))
