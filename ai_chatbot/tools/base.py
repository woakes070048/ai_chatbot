# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Base Tool Module
Backward-compatible wrapper around the tool registry.

chat.py imports `get_all_tools_schema` and `BaseTool.execute_tool` from here.
Both now delegate to the registry.

Phase 12A adds ``get_tools_for_message()`` which routes queries to a relevant
tool subset instead of sending all tools on every request.
"""

from __future__ import annotations

from ai_chatbot.tools.registry import execute_tool as _registry_execute_tool
from ai_chatbot.tools.registry import get_all_tools_schema as _registry_get_all_tools_schema


class BaseTool:
	"""Backward-compatible base class. Delegates to the registry."""

	@staticmethod
	def execute_tool(tool_name: str, arguments: dict) -> dict:
		"""Execute a tool by name via the registry."""
		return _registry_execute_tool(tool_name, arguments)


def get_all_tools_schema() -> list[dict]:
	"""Get combined schema from all enabled tool modules via the registry."""
	return _registry_get_all_tools_schema()


def get_tools_for_message(
	user_message: str,
	conversation_history: list[dict] | None = None,
) -> tuple[list[dict], object]:
	"""Get tools relevant to a specific user message.

	Uses the Phase 12A tool router to classify the query intent and
	return only the matching tool subset.  Falls back to all tools
	when no confident category match is found.

	This replaces ``get_all_tools_schema()`` as the primary tool
	selection entry point in ``api/chat.py`` and ``api/streaming.py``.

	Args:
		user_message: The user's message text.
		conversation_history: Optional conversation history for
			follow-up detection.

	Returns:
		Tuple of (tool_schemas, ToolRoutingResult).
	"""
	from ai_chatbot.core.tool_router import route_tools

	result = route_tools(user_message, conversation_history)
	return result.tools, result
