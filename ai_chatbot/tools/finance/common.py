# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Common Finance Helpers
Shared utilities for finance tool modules — eliminates duplication across files.

`primary` and `apply_company_filter` are re-exported from `ai_chatbot.tools.common`
so existing finance imports continue to work unchanged.
"""

from __future__ import annotations

from ai_chatbot.core.constants import AGING_BUCKETS
from ai_chatbot.tools.common import apply_company_filter, primary


def get_aging_bucket(days_overdue: int) -> str:
	"""Classify days overdue into an aging bucket label.

	Uses the AGING_BUCKETS constant (0-30, 31-60, 61-90, 90+).

	Args:
		days_overdue: Number of days overdue (non-negative).

	Returns:
		Bucket label string (e.g. "0-30", "31-60", "61-90", "90+").
	"""
	for bucket in AGING_BUCKETS:
		if bucket["max"] is None:
			if days_overdue >= bucket["min"]:
				return bucket["label"]
		elif bucket["min"] <= days_overdue <= bucket["max"]:
			return bucket["label"]
	return "90+"
