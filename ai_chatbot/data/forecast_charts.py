# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Forecast-Specific ECharts Builders

Builds ECharts options for time-series forecasts with:
- Historical data (solid line)
- Forecast data (dashed line)
- Confidence interval bands (semi-transparent area)
- Boundary marker between historical and forecast periods
"""

from frappe.utils import flt

from ai_chatbot.data.charts import CHART_COLORS


def build_forecast_chart(
	title: str,
	historical_labels: list[str],
	historical_values: list[float],
	forecast_labels: list[str],
	forecast_values: list[float],
	confidence_95: list[tuple[float, float]],
	y_axis_name: str = "",
) -> dict:
	"""Build a forecast line chart with confidence band.

	The chart shows:
	- Solid line for historical data
	- Dashed line for forecast data (connected at boundary)
	- Semi-transparent area band for 95% confidence interval
	- Vertical marker at the historical/forecast boundary

	Args:
		title: Chart title.
		historical_labels: Month labels for historical data.
		historical_values: Historical data values.
		forecast_labels: Month labels for forecast data.
		forecast_values: Forecast data values.
		confidence_95: List of (low, high) tuples for 95% confidence.
		y_axis_name: Y-axis label.

	Returns:
		Complete ECharts option dict.
	"""
	all_labels = historical_labels + forecast_labels
	n_hist = len(historical_labels)

	# Historical series: values for hist portion, None for forecast portion
	hist_data = [flt(v, 2) for v in historical_values] + [None] * len(forecast_labels)

	# Forecast series: None for hist portion (except last point for line continuity),
	# then forecast values
	forecast_data = (
		[None] * (n_hist - 1) + [flt(historical_values[-1], 2)] + [flt(v, 2) for v in forecast_values]
	)

	# Confidence bands: upper and lower bounds (only for forecast region)
	# Use None for historical portion to avoid rendering bands there
	upper_data = [None] * n_hist + [flt(hi, 2) for _, hi in confidence_95]
	lower_data = [None] * n_hist + [flt(lo, 2) for lo, _ in confidence_95]

	return {
		"color": CHART_COLORS,
		"title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
		"tooltip": {"trigger": "axis"},
		"legend": {"bottom": 0, "data": ["Historical", "Forecast", "95% Confidence"]},
		"grid": {"left": "15%", "right": "5%", "bottom": "15%", "top": "22%"},
		"xAxis": {
			"type": "category",
			"data": all_labels,
			"axisLabel": {"fontSize": 11, "rotate": 30 if len(all_labels) > 12 else 0},
		},
		"yAxis": {"type": "value", "name": y_axis_name, "nameGap": 10},
		"series": [
			{
				"name": "Historical",
				"type": "line",
				"data": hist_data,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[0]},
				"lineStyle": {"width": 2},
				"symbol": "circle",
				"symbolSize": 4,
			},
			{
				"name": "Forecast",
				"type": "line",
				"data": forecast_data,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[3]},
				"lineStyle": {"width": 2, "type": "dashed"},
				"symbol": "circle",
				"symbolSize": 4,
				"markLine": {
					"silent": True,
					"data": [{"xAxis": historical_labels[-1]}],
					"lineStyle": {"color": "#999", "type": "dashed", "width": 1},
					"label": {"show": False},
					"symbol": "none",
				},
			},
			{
				"name": "95% Confidence",
				"type": "line",
				"data": upper_data,
				"smooth": True,
				"lineStyle": {"opacity": 0},
				"areaStyle": {"opacity": 0},
				"stack": "confidence",
				"symbol": "none",
			},
			{
				"name": "",
				"type": "line",
				"data": lower_data,
				"smooth": True,
				"lineStyle": {"opacity": 0},
				"areaStyle": {"opacity": 0.15, "color": CHART_COLORS[3]},
				"stack": "confidence",
				"symbol": "none",
			},
		],
	}


def build_cash_flow_forecast_chart(
	historical_labels: list[str],
	historical_inflows: list[float],
	historical_outflows: list[float],
	forecast_labels: list[str],
	forecast_inflows: list[float],
	forecast_outflows: list[float],
) -> dict:
	"""Build a multi-series chart for cash flow forecast.

	Shows historical and forecast as separate visual segments
	(solid vs dashed) for both inflow and outflow series, plus net cash flow.

	Args:
		historical_labels: Month labels for historical data.
		historical_inflows: Historical inflow values.
		historical_outflows: Historical outflow values.
		forecast_labels: Month labels for forecast data.
		forecast_inflows: Forecast inflow values.
		forecast_outflows: Forecast outflow values.

	Returns:
		Complete ECharts option dict.
	"""
	all_labels = historical_labels + forecast_labels
	n_hist = len(historical_labels)
	n_fore = len(forecast_labels)

	# Historical net
	hist_net = [flt(i - o, 2) for i, o in zip(historical_inflows, historical_outflows, strict=True)]

	# Forecast net
	fore_net = [flt(i - o, 2) for i, o in zip(forecast_inflows, forecast_outflows, strict=True)]

	# Build series data: hist portion solid, forecast portion dashed
	# Inflow historical (solid)
	inflow_hist = [flt(v, 2) for v in historical_inflows] + [None] * n_fore
	# Inflow forecast (dashed, connected at boundary)
	inflow_fore = (
		[None] * (n_hist - 1) + [flt(historical_inflows[-1], 2)] + [flt(v, 2) for v in forecast_inflows]
	)

	# Outflow historical (solid)
	outflow_hist = [flt(v, 2) for v in historical_outflows] + [None] * n_fore
	# Outflow forecast (dashed, connected at boundary)
	outflow_fore = (
		[None] * (n_hist - 1) + [flt(historical_outflows[-1], 2)] + [flt(v, 2) for v in forecast_outflows]
	)

	# Net historical (solid)
	net_hist = [flt(v, 2) for v in hist_net] + [None] * n_fore
	# Net forecast (dashed, connected at boundary)
	net_fore = [None] * (n_hist - 1) + [flt(hist_net[-1], 2)] + [flt(v, 2) for v in fore_net]

	return {
		"color": CHART_COLORS,
		"title": {"text": "Cash Flow Forecast", "left": "center", "textStyle": {"fontSize": 14}},
		"tooltip": {"trigger": "axis"},
		"legend": {
			"bottom": 0,
			"data": [
				"Inflow",
				"Inflow (forecast)",
				"Outflow",
				"Outflow (forecast)",
				"Net",
				"Net (forecast)",
			],
		},
		"grid": {"left": "15%", "right": "5%", "bottom": "18%", "top": "22%"},
		"xAxis": {
			"type": "category",
			"data": all_labels,
			"axisLabel": {"fontSize": 11, "rotate": 30 if len(all_labels) > 12 else 0},
		},
		"yAxis": {"type": "value", "name": "Amount", "nameGap": 10},
		"series": [
			{
				"name": "Inflow",
				"type": "line",
				"data": inflow_hist,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[1]},
				"lineStyle": {"width": 2},
			},
			{
				"name": "Inflow (forecast)",
				"type": "line",
				"data": inflow_fore,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[1]},
				"lineStyle": {"width": 2, "type": "dashed"},
			},
			{
				"name": "Outflow",
				"type": "line",
				"data": outflow_hist,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[3]},
				"lineStyle": {"width": 2},
			},
			{
				"name": "Outflow (forecast)",
				"type": "line",
				"data": outflow_fore,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[3]},
				"lineStyle": {"width": 2, "type": "dashed"},
			},
			{
				"name": "Net",
				"type": "line",
				"data": net_hist,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[0]},
				"lineStyle": {"width": 2},
			},
			{
				"name": "Net (forecast)",
				"type": "line",
				"data": net_fore,
				"smooth": True,
				"itemStyle": {"color": CHART_COLORS[0]},
				"lineStyle": {"width": 2, "type": "dashed"},
				"markLine": {
					"silent": True,
					"data": [{"xAxis": historical_labels[-1]}],
					"lineStyle": {"color": "#999", "type": "dashed", "width": 1},
					"label": {"show": False},
					"symbol": "none",
				},
			},
		],
	}
