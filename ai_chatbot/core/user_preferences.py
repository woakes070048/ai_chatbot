# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
User Preference Memory for AI Chatbot (Phase 14B.2)

Tracks per-user preferences that persist across conversations. Preferences
are learned from tool usage patterns and explicit user requests, then
injected into the system prompt to personalise responses.

Storage: JSON field ``user_preferences`` on the ``Chatbot Settings`` Single
DocType, keyed by ``frappe.session.user``.

Tracked preferences:
- preferred_format: "table" | "chart" | "both" | None
- preferred_currency_display: "base" | "transaction" | None
- frequent_topics: list of topic labels the user often queries
- frequent_tools: list of tool names the user triggers most
- language: response language preference (also in session_context)
"""

from __future__ import annotations

import json

import frappe

# Maximum number of entries in list-type preferences
_MAX_FREQUENT_TOPICS = 10
_MAX_FREQUENT_TOOLS = 10

# Valid values for enum-like preferences
_VALID_FORMATS = {"table", "chart", "both"}
_VALID_CURRENCY_DISPLAY = {"base", "transaction"}


def get_user_preferences(user: str | None = None) -> dict:
	"""Get stored preferences for a user.

	Args:
		user: Frappe user ID. Defaults to current session user.

	Returns:
		Dict of preferences with sensible defaults.
	"""
	user = user or frappe.session.user
	defaults = {
		"preferred_format": None,
		"preferred_currency_display": None,
		"frequent_topics": [],
		"frequent_tools": [],
		"language": None,
	}

	try:
		raw = frappe.db.get_single_value("Chatbot Settings", "user_preferences")
		if raw:
			all_prefs = json.loads(raw) if isinstance(raw, str) else raw
			if isinstance(all_prefs, dict):
				user_prefs = all_prefs.get(user, {})
				return {**defaults, **user_prefs}
	except Exception:
		pass

	return defaults


def set_user_preference(key: str, value, user: str | None = None) -> dict:
	"""Set a single user preference.

	Args:
		key: Preference key (e.g. "preferred_format").
		value: Value to set.
		user: Frappe user ID. Defaults to current session user.

	Returns:
		Updated preferences dict for the user.
	"""
	user = user or frappe.session.user
	all_prefs = _load_all_preferences()
	user_prefs = all_prefs.get(user, {})
	user_prefs[key] = value
	all_prefs[user] = user_prefs
	_save_all_preferences(all_prefs)
	return user_prefs


def record_tool_usage(tool_name: str, user: str | None = None) -> None:
	"""Record that a tool was used, updating the frequent_tools list.

	Maintains a frequency-ordered list of the user's most-used tools.
	Called from the tool execution path.

	Args:
		tool_name: Name of the tool that was executed.
		user: Frappe user ID. Defaults to current session user.
	"""
	user = user or frappe.session.user
	all_prefs = _load_all_preferences()
	user_prefs = all_prefs.get(user, {})

	tools = user_prefs.get("frequent_tools", [])

	# Move to front if already present, otherwise prepend
	if tool_name in tools:
		tools.remove(tool_name)
	tools.insert(0, tool_name)

	user_prefs["frequent_tools"] = tools[:_MAX_FREQUENT_TOOLS]
	all_prefs[user] = user_prefs
	_save_all_preferences(all_prefs)


def record_topic(topic: str, user: str | None = None) -> None:
	"""Record a conversation topic, updating the frequent_topics list.

	Called from the summarisation pipeline when topics are extracted.

	Args:
		topic: Short topic label (2-4 words).
		user: Frappe user ID. Defaults to current session user.
	"""
	user = user or frappe.session.user
	all_prefs = _load_all_preferences()
	user_prefs = all_prefs.get(user, {})

	topics = user_prefs.get("frequent_topics", [])

	# Move to front if already present, otherwise prepend
	topic_lower = topic.lower().strip()
	# Deduplicate case-insensitively
	topics = [t for t in topics if t.lower().strip() != topic_lower]
	topics.insert(0, topic)

	user_prefs["frequent_topics"] = topics[:_MAX_FREQUENT_TOPICS]
	all_prefs[user] = user_prefs
	_save_all_preferences(all_prefs)


def build_preferences_prompt_block(user: str | None = None) -> str | None:
	"""Build the user preferences block for the system prompt.

	Returns None if there are no meaningful preferences to include
	(avoids wasting tokens on empty blocks).

	Args:
		user: Frappe user ID. Defaults to current session user.

	Returns:
		Formatted preferences string, or None.
	"""
	prefs = get_user_preferences(user)
	parts: list[str] = []

	fmt = prefs.get("preferred_format")
	if fmt and fmt in _VALID_FORMATS:
		labels = {"table": "data tables", "chart": "charts/visualizations", "both": "charts with data tables"}
		parts.append(f"- Preferred format: {labels.get(fmt, fmt)}")

	currency = prefs.get("preferred_currency_display")
	if currency and currency in _VALID_CURRENCY_DISPLAY:
		labels = {"base": "company base currency", "transaction": "original transaction currency"}
		parts.append(f"- Preferred currency display: {labels.get(currency, currency)}")

	lang = prefs.get("language")
	if lang:
		parts.append(f"- Preferred language: {lang}")

	topics = prefs.get("frequent_topics", [])
	if topics:
		parts.append(f"- Frequently asks about: {', '.join(topics[:5])}")

	tools = prefs.get("frequent_tools", [])
	if tools:
		# Show human-readable tool names (replace underscores, take top 5)
		readable = [t.replace("_", " ") for t in tools[:5]]
		parts.append(f"- Most used tools: {', '.join(readable)}")

	if not parts:
		return None

	return "## User Preferences (learned)\n" + "\n".join(parts)


# ── Internal helpers ────────────────────────────────────────────────


def _load_all_preferences() -> dict:
	"""Load the full user_preferences JSON from Chatbot Settings."""
	try:
		raw = frappe.db.get_single_value("Chatbot Settings", "user_preferences")
		if raw:
			parsed = json.loads(raw) if isinstance(raw, str) else raw
			if isinstance(parsed, dict):
				return parsed
	except Exception:
		pass
	return {}


def _save_all_preferences(all_prefs: dict) -> None:
	"""Save the full user_preferences JSON to Chatbot Settings."""
	frappe.db.set_single_value(
		"Chatbot Settings",
		"user_preferences",
		json.dumps(all_prefs),
		update_modified=False,
	)
