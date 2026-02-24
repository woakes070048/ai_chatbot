# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Token Optimization Module

Strategies to reduce token usage and stay within context limits:
1. Conversation history trimming — keep only the last N messages
2. Tool result compression — strip verbose metadata, remove echart_option
3. Structured data truncation — cap large datasets to max_rows
"""

import json

import frappe


def trim_conversation_history(messages: list[dict], max_messages: int = 20) -> list[dict]:
	"""Keep system prompt + last N messages.

	Preserves the system message (always first) and trims older messages
	from the conversation history to reduce token usage.

	Args:
		messages: Full message list (system + user/assistant/tool).
		max_messages: Maximum non-system messages to keep. 0 = unlimited.

	Returns:
		Trimmed message list.
	"""
	if max_messages <= 0:
		return messages

	system = [m for m in messages if m.get("role") == "system"]
	history = [m for m in messages if m.get("role") != "system"]

	if len(history) <= max_messages:
		return messages

	return system + history[-max_messages:]


def compress_tool_result(result: dict, max_rows: int = 20) -> dict:
	"""Compress a tool result dict to reduce token usage.

	- Truncates large data arrays to max_rows
	- Removes echart_option (frontend renders it; AI doesn't need it)
	- Strips empty or None values

	Args:
		result: Tool result dict (typically from BaseTool.execute_tool).
		max_rows: Maximum rows to keep in data arrays.

	Returns:
		Compressed result dict.
	"""
	if not isinstance(result, dict):
		return result

	compressed = dict(result)

	# Remove echart_option — frontend renders charts from it, AI doesn't need it
	compressed.pop("echart_option", None)

	# Truncate large data arrays
	if isinstance(compressed.get("data"), list) and len(compressed["data"]) > max_rows:
		total = len(compressed["data"])
		compressed["data"] = compressed["data"][:max_rows]
		compressed["_truncated"] = True
		compressed["_total_rows"] = total

	return compressed


def compress_tool_results_in_history(history: list[dict], max_rows: int = 20) -> list[dict]:
	"""Compress tool result messages in conversation history.

	Finds messages with role="tool" and compresses their JSON content.

	Args:
		history: Message list to process.
		max_rows: Maximum data rows per tool result.

	Returns:
		History with compressed tool results.
	"""
	compressed = []
	for msg in history:
		if msg.get("role") == "tool" and msg.get("content"):
			try:
				content = json.loads(msg["content"]) if isinstance(msg["content"], str) else msg["content"]
				if isinstance(content, dict):
					content = compress_tool_result(content, max_rows)
					compressed.append({**msg, "content": json.dumps(content)})
					continue
			except (json.JSONDecodeError, TypeError):
				pass
		compressed.append(msg)
	return compressed


def get_max_context_messages() -> int:
	"""Get the max_context_messages setting, with fallback to default 20."""
	try:
		settings = frappe.get_single("Chatbot Settings")
		return getattr(settings, "max_context_messages", 20) or 20
	except Exception:
		return 20


def optimize_history(messages: list[dict]) -> list[dict]:
	"""Apply all optimization strategies to a message history.

	1. Trim to max_context_messages
	2. Compress tool results

	Args:
		messages: Full message list including system prompt.

	Returns:
		Optimized message list.
	"""
	max_msgs = get_max_context_messages()
	optimized = trim_conversation_history(messages, max_msgs)
	optimized = compress_tool_results_in_history(optimized)
	return optimized
