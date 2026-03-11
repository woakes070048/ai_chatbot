# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Statistical Forecasting Engine for AI Chatbot

Pure-Python implementations of time-series forecasting algorithms.
numpy is used when available for faster computation, but all algorithms
have pure-Python fallbacks.

Algorithms:
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA) / Exponential Smoothing
- Linear Regression (least squares) for trend detection
- Additive/Multiplicative Seasonal Decomposition
- Confidence Intervals (based on historical residual std dev)
- Z-score and IQR anomaly detection
"""

import math

from ai_chatbot.core.constants import MIN_FORECAST_HISTORY
from ai_chatbot.core.exceptions import InsufficientDataError

# --- Optional numpy ---
try:
	import numpy as np

	HAS_NUMPY = True
except ImportError:
	HAS_NUMPY = False


# Z-scores for confidence levels
Z_SCORES = {0.80: 1.282, 0.95: 1.960}
SEASONALITY_PERIOD = 12  # monthly seasonality


# ──────────────────────────────────────────────────────────────────────
# Basic Statistics Helpers
# ──────────────────────────────────────────────────────────────────────


def _mean(values: list[float]) -> float:
	"""Compute arithmetic mean."""
	if not values:
		return 0.0
	if HAS_NUMPY:
		return float(np.mean(values))
	return sum(values) / len(values)


def _std(values: list[float], ddof: int = 1) -> float:
	"""Compute standard deviation with given degrees of freedom."""
	if len(values) < 2:
		return 0.0
	if HAS_NUMPY:
		return float(np.std(values, ddof=ddof))
	m = _mean(values)
	variance = sum((x - m) ** 2 for x in values) / (len(values) - ddof)
	return math.sqrt(max(variance, 0))


def _median(values: list[float]) -> float:
	"""Compute median."""
	if not values:
		return 0.0
	s = sorted(values)
	n = len(s)
	mid = n // 2
	if n % 2 == 0:
		return (s[mid - 1] + s[mid]) / 2
	return s[mid]


# ──────────────────────────────────────────────────────────────────────
# Core Forecasting Methods
# ──────────────────────────────────────────────────────────────────────


def simple_moving_average(values: list[float], window: int = 3) -> float:
	"""Compute the SMA over the last `window` values.

	Args:
		values: Historical time series.
		window: Number of periods to average.

	Returns:
		The moving average value.
	"""
	if not values:
		return 0.0
	window = min(window, len(values))
	return _mean(values[-window:])


def exponential_moving_average(values: list[float], alpha: float = 0.3) -> list[float]:
	"""Compute EMA series using exponential smoothing.

	Args:
		values: Historical time series.
		alpha: Smoothing factor (0 < alpha <= 1). Higher = more weight on recent.

	Returns:
		List of EMA values, same length as input.
	"""
	if not values:
		return []

	ema = [values[0]]
	for i in range(1, len(values)):
		ema.append(alpha * values[i] + (1 - alpha) * ema[i - 1])
	return ema


def linear_regression(values: list[float]) -> tuple[float, float]:
	"""Least-squares linear regression on sequential indices.

	Fits y = slope * x + intercept where x is the 0-indexed position.

	Args:
		values: Historical time series.

	Returns:
		(slope, intercept) tuple.
	"""
	n = len(values)
	if n < 2:
		return (0.0, values[0] if values else 0.0)

	if HAS_NUMPY:
		x = np.arange(n, dtype=float)
		y = np.array(values, dtype=float)
		coeffs = np.polyfit(x, y, 1)
		return (float(coeffs[0]), float(coeffs[1]))

	# Pure Python least squares
	x_mean = (n - 1) / 2.0
	y_mean = _mean(values)

	numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
	denominator = sum((i - x_mean) ** 2 for i in range(n))

	if denominator == 0:
		return (0.0, y_mean)

	slope = numerator / denominator
	intercept = y_mean - slope * x_mean
	return (slope, intercept)


def detect_seasonality(values: list[float], period: int = SEASONALITY_PERIOD) -> list[float] | None:
	"""Detect repeating seasonal pattern using multiplicative decomposition.

	Computes seasonal factors: one per period position. Each factor is the
	average of values at that position relative to the overall mean.

	Args:
		values: Historical time series (monthly).
		period: Expected cycle length (default 12 for monthly data).

	Returns:
		List of `period` seasonal factors if enough data, otherwise None.
		A factor of 1.0 means no seasonal effect at that position.
	"""
	if len(values) < period:
		return None

	overall_mean = _mean(values)
	if overall_mean == 0:
		return None

	# Compute average value at each position in the cycle
	position_values: dict[int, list[float]] = {i: [] for i in range(period)}
	for i, v in enumerate(values):
		position_values[i % period].append(v)

	factors = []
	for pos in range(period):
		pos_mean = _mean(position_values[pos])
		factors.append(pos_mean / overall_mean if overall_mean != 0 else 1.0)

	return factors


# ──────────────────────────────────────────────────────────────────────
# Main Forecasting Entry Point
# ──────────────────────────────────────────────────────────────────────


def forecast_time_series(
	values: list[float],
	months_ahead: int = 3,
	method: str = "auto",
) -> dict:
	"""Main forecasting entry point.

	Args:
		values: Monthly historical values (oldest first).
		months_ahead: Number of future months to predict.
		method: "sma", "ema", "linear", "seasonal", or "auto".

	Returns:
		Dict with forecast, confidence bands, method info, and trend.

	Raises:
		InsufficientDataError: If fewer than MIN_FORECAST_HISTORY data points.
	"""
	n = len(values)
	if n < MIN_FORECAST_HISTORY:
		raise InsufficientDataError(required_months=MIN_FORECAST_HISTORY, available_months=n)

	# Compute statistics
	slope, intercept = linear_regression(values)
	mean = _mean(values)
	std = _std(values)
	seasonal_factors = detect_seasonality(values)

	# Determine trend
	if mean != 0:
		trend_strength = abs(slope) / (abs(mean) + 1e-9)
	else:
		trend_strength = 0.0

	has_trend = trend_strength > 0.02  # >2% of mean per month
	has_seasonality = False
	if seasonal_factors:
		max_deviation = max(abs(sf - 1.0) for sf in seasonal_factors)
		has_seasonality = max_deviation > 0.10  # >10% seasonal swing

	# Method selection
	if method == "auto":
		if has_seasonality and n >= 24:
			method = "seasonal"
		elif has_trend and n >= 6:
			method = "linear"
		elif n >= 6:
			method = "ema"
		else:
			method = "sma"

	# Generate forecast based on selected method
	forecast = _generate_forecast(
		values=values,
		method=method,
		months_ahead=months_ahead,
		slope=slope,
		intercept=intercept,
		seasonal_factors=seasonal_factors,
		has_trend=has_trend,
	)

	# Clamp to non-negative
	forecast = [max(0.0, v) for v in forecast]

	# Compute confidence intervals
	confidence = compute_confidence_intervals(forecast, values, method, slope, intercept)

	# Determine trend direction
	if slope > 0 and has_trend:
		trend = "increasing"
	elif slope < 0 and has_trend:
		trend = "decreasing"
	else:
		trend = "stable"

	return {
		"forecast": forecast,
		"confidence_80": confidence[0.80],
		"confidence_95": confidence[0.95],
		"method_used": method,
		"trend": trend,
		"seasonality_detected": has_seasonality,
		"historical_mean": round(mean, 2),
		"historical_std": round(std, 2),
	}


def _generate_forecast(
	values: list[float],
	method: str,
	months_ahead: int,
	slope: float,
	intercept: float,
	seasonal_factors: list[float] | None,
	has_trend: bool,
) -> list[float]:
	"""Generate forecast values using the specified method."""
	n = len(values)
	forecast = []

	if method == "seasonal" and seasonal_factors:
		# Linear trend + seasonal factors
		for i in range(months_ahead):
			base = slope * (n + i) + intercept
			season_idx = (n + i) % len(seasonal_factors)
			forecast.append(base * seasonal_factors[season_idx])

	elif method == "linear":
		for i in range(months_ahead):
			forecast.append(slope * (n + i) + intercept)

	elif method == "ema":
		alpha = 2.0 / (min(n, 6) + 1)
		ema_series = exponential_moving_average(values, alpha)
		last_ema = ema_series[-1]
		for i in range(months_ahead):
			val = last_ema
			# Apply damped trend if detected
			if has_trend:
				val += slope * (i + 1) * 0.5
			forecast.append(val)

	else:  # sma
		window = min(n, 6)
		sma_val = simple_moving_average(values, window)
		forecast = [sma_val] * months_ahead

	return forecast


# ──────────────────────────────────────────────────────────────────────
# Confidence Intervals
# ──────────────────────────────────────────────────────────────────────


def compute_confidence_intervals(
	forecast: list[float],
	historical_values: list[float],
	method: str,
	slope: float,
	intercept: float,
) -> dict[float, list[tuple[float, float]]]:
	"""Compute confidence intervals based on historical residual variance.

	Uses the standard deviation of residuals (actual vs fitted) to project
	uncertainty bands that grow with forecast horizon.

	Returns:
		Dict mapping confidence level to list of (low, high) tuples.
	"""
	n = len(historical_values)

	# Compute residuals from the fitted model
	if method == "linear" or method == "seasonal":
		fitted = [slope * i + intercept for i in range(n)]
	elif method == "ema":
		alpha = 2.0 / (min(n, 6) + 1)
		fitted = exponential_moving_average(historical_values, alpha)
	else:
		window = min(n, 6)
		avg = simple_moving_average(historical_values, window)
		fitted = [avg] * n

	residuals = [historical_values[i] - fitted[i] for i in range(n)]
	residual_std = _std(residuals, ddof=1) if len(residuals) >= 2 else _std(historical_values, ddof=1)

	# Ensure a minimum uncertainty (avoid zero-width bands)
	if residual_std < 1e-6:
		residual_std = _std(historical_values, ddof=1) * 0.1

	result = {}
	for level, z in Z_SCORES.items():
		bands = []
		for i, fv in enumerate(forecast):
			# Uncertainty grows with forecast horizon
			uncertainty = residual_std * math.sqrt(1 + (i + 1) * 0.15)
			low = max(0.0, fv - z * uncertainty)
			high = fv + z * uncertainty
			bands.append((round(low, 2), round(high, 2)))
		result[level] = bands

	return result


# ──────────────────────────────────────────────────────────────────────
# Anomaly Detection Helpers
# ──────────────────────────────────────────────────────────────────────


def z_score_anomalies(values: list[float], threshold: float = 2.5) -> list[int]:
	"""Return indices of values whose absolute z-score exceeds threshold.

	Args:
		values: List of numeric values.
		threshold: Z-score cutoff (default 2.5).

	Returns:
		List of indices flagged as anomalies.
	"""
	if len(values) < 3:
		return []

	mean = _mean(values)
	std = _std(values)
	if std < 1e-9:
		return []

	return [i for i, v in enumerate(values) if abs((v - mean) / std) > threshold]


def iqr_anomalies(values: list[float], multiplier: float = 1.5) -> list[int]:
	"""Return indices of values outside the IQR fence.

	Args:
		values: List of numeric values.
		multiplier: IQR multiplier for fence (default 1.5).

	Returns:
		List of indices flagged as anomalies.
	"""
	if len(values) < 4:
		return []

	sorted_vals = sorted(values)
	n = len(sorted_vals)
	q1 = sorted_vals[n // 4]
	q3 = sorted_vals[3 * n // 4]
	iqr = q3 - q1

	if iqr < 1e-9:
		return []

	lower = q1 - multiplier * iqr
	upper = q3 + multiplier * iqr

	return [i for i, v in enumerate(values) if v < lower or v > upper]


# ──────────────────────────────────────────────────────────────────────
# Month Utilities
# ──────────────────────────────────────────────────────────────────────


def generate_month_labels(start_label: str, count: int) -> list[str]:
	"""Generate sequential YYYY-MM labels starting after start_label.

	Args:
		start_label: The last historical month label, e.g. "2026-02".
		count: Number of future months to generate.

	Returns:
		List of month labels, e.g. ["2026-03", "2026-04", "2026-05"].
	"""
	year, month = int(start_label[:4]), int(start_label[5:7])
	labels = []
	for _ in range(count):
		month += 1
		if month > 12:
			month = 1
			year += 1
		labels.append(f"{year:04d}-{month:02d}")
	return labels


def fill_month_gaps(
	rows: list[dict],
	month_field: str,
	value_field: str,
	start_month: str,
	total_months: int,
) -> tuple[list[str], list[float]]:
	"""Fill gaps in monthly query results with zeros.

	Takes sparse query results and returns dense aligned lists
	covering the full range.

	Args:
		rows: Query results with month and value fields.
		month_field: Key name for the month label in each row.
		value_field: Key name for the numeric value in each row.
		start_month: First month to include (YYYY-MM).
		total_months: Total months to cover.

	Returns:
		(labels, values) — parallel lists with zeros for missing months.
	"""
	from frappe.utils import flt

	value_map = {r[month_field]: flt(r[value_field]) for r in rows}

	labels = []
	values = []
	year, month = int(start_month[:4]), int(start_month[5:7])

	for _ in range(total_months):
		label = f"{year:04d}-{month:02d}"
		labels.append(label)
		values.append(value_map.get(label, 0.0))
		month += 1
		if month > 12:
			month = 1
			year += 1

	return labels, values
