# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Conversation History Reconstruction

Loads stored Chatbot Message records and rebuilds an LLM-ready history list,
including multimodal attachments and tool call/result exchanges.
"""

import json

import frappe


def _normalize_tool_call(tc: dict) -> dict:
	"""Normalize a stored tool call to OpenAI format.

	Handles three stored formats:
	- Streaming normalized: {id, name, arguments} (arguments is dict)
	- Non-streaming OpenAI: {id, type, function: {name, arguments}} (arguments is JSON string)
	- Non-streaming Claude: {type: "tool_use", id, name, input}
	"""
	if "function" in tc:
		# Already OpenAI format
		return tc
	name = tc.get("name", "")
	args = tc.get("arguments") or tc.get("input") or {}
	if isinstance(args, str):
		args = json.loads(args)
	return {
		"id": tc.get("id", ""),
		"type": "function",
		"function": {
			"name": name,
			"arguments": json.dumps(args) if isinstance(args, dict) else args,
		},
	}


def get_conversation_history(conversation_id: str) -> list[dict]:
	"""Get conversation history in AI message format.

	For messages with image attachments, builds multimodal content arrays
	using the OpenAI Vision format (converted to Claude format by the provider).

	For assistant messages with tool_calls, reconstructs the full tool call/result
	exchange so the LLM sees the correct conversation structure on subsequent turns.
	"""
	messages = frappe.get_all(
		"Chatbot Message",
		filters={"conversation": conversation_id},
		fields=["role", "content", "tool_calls", "tool_results", "attachments"],
		order_by="timestamp asc",
	)

	history = []
	for msg in messages:
		# Check if user message has attachments — build appropriate content
		if msg.role == "user" and msg.attachments:
			try:
				atts = json.loads(msg.attachments) if isinstance(msg.attachments, str) else msg.attachments
			except (json.JSONDecodeError, TypeError):
				atts = None

			if atts:
				has_images = any(a.get("is_image") for a in atts)
				if has_images:
					# Image attachments: use multimodal Vision content
					from ai_chatbot.api.files import build_vision_content

					content = build_vision_content(msg.content or "", atts)
					history.append({"role": msg.role, "content": content})
				else:
					# Non-image attachments (PDF, Excel, etc.): append file refs
					# so the LLM knows the file_url for IDP tools
					text = msg.content or ""
					for att in atts:
						file_url = att.get("file_url", "")
						file_name = att.get("file_name", "unknown")
						mime_type = att.get("mime_type", "")
						text += f"\n[Attached file: {file_name} ({mime_type}), file_url: {file_url}]"
					history.append({"role": msg.role, "content": text})
				continue

		# Reconstruct tool call/result exchange for assistant messages
		if msg.role == "assistant" and msg.tool_calls:
			try:
				raw_tcs = json.loads(msg.tool_calls) if isinstance(msg.tool_calls, str) else msg.tool_calls
			except (json.JSONDecodeError, TypeError):
				raw_tcs = None

			if raw_tcs:
				openai_tcs = [_normalize_tool_call(tc) for tc in raw_tcs]
				history.append(
					{
						"role": "assistant",
						"content": msg.content or None,
						"tool_calls": openai_tcs,
					}
				)

				# Inject tool result messages
				try:
					raw_results = (
						json.loads(msg.tool_results)
						if isinstance(msg.tool_results, str)
						else msg.tool_results
					) or []
				except (json.JSONDecodeError, TypeError):
					raw_results = []

				for i, tc in enumerate(openai_tcs):
					result_content = json.dumps(raw_results[i]) if i < len(raw_results) else "{}"
					history.append(
						{
							"role": "tool",
							"content": result_content,
							"tool_call_id": tc["id"],
						}
					)
				continue

		message_dict = {"role": msg.role, "content": msg.content}
		history.append(message_dict)

	return history
