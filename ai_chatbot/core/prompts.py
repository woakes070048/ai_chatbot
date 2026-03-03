# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
System Prompt Builder for AI Chatbot

Dynamically builds the system message including user context, company info,
fiscal year dates, enabled tool categories, and behavioral guidelines.
"""

import frappe
from frappe.utils import nowdate

from ai_chatbot.core.config import (
	get_company_currency,
	get_default_company,
	get_fiscal_year_dates,
)
from ai_chatbot.core.constants import TOOL_CATEGORIES


def build_system_prompt(conversation_id: str | None = None):
	"""Build the system prompt with dynamic context.

	Includes:
	- ERPNext assistant persona (configurable)
	- Current user name, company, currency, fiscal year dates
	- Guidelines for default date ranges and currency handling
	- Enabled tool categories
	- Accounting dimension filtering context
	- Multi-company consolidation context (if parent company)
	- Current session state (include_subsidiaries, target_currency)
	- Write operation confirmation rules (if enabled)
	- Response language (configurable)
	- Custom system prompt and instructions (configurable)
	- Response format guidelines

	Args:
		conversation_id: Optional conversation ID to read session context.

	Returns:
		str: The complete system prompt.
	"""
	parts = []
	settings = frappe.get_single("Chatbot Settings")
	company = None

	# --- Persona (configurable) ---
	persona = (getattr(settings, "ai_persona", "") or "").strip()
	if not persona:
		persona = "an intelligent ERPNext business assistant"

	parts.append(
		f"You are {persona}. "
		"You help users analyze business data, manage records, and get insights "
		"from their ERPNext system."
	)

	# --- User & Company Context ---
	try:
		user = frappe.session.user
		full_name = frappe.db.get_value("User", user, "full_name") or user
		company = get_default_company()
		currency = get_company_currency(company)
		fy_from, fy_to = get_fiscal_year_dates(company)

		parts.append(
			f"\n## Current Context\n"
			f"- **User**: {full_name}\n"
			f"- **Company**: {company}\n"
			f"- **Currency**: {currency}\n"
			f"- **Fiscal Year**: {fy_from} to {fy_to}\n"
			f"- **Today**: {nowdate()}"
		)
	except Exception:
		parts.append(f"\n## Current Context\n- **Today**: {nowdate()}")

	# --- Multi-Company / Session Context ---
	if company:
		try:
			from ai_chatbot.core.consolidation import get_child_companies, is_parent_company

			if is_parent_company(company):
				children = get_child_companies(company)
				if children:
					child_list = ", ".join(children[:10])
					suffix = f" (and {len(children) - 10} more)" if len(children) > 10 else ""
					parent_currency = get_company_currency(company)

					# Read current session state
					session_state = ""
					if conversation_id:
						from ai_chatbot.core.session_context import get_session_context

						ctx = get_session_context(conversation_id)
						inc_subs = ctx.get("include_subsidiaries", False)
						tgt_curr = ctx.get("target_currency")
						session_state = (
							f"\n- **Current session state:**\n"
							f"  - `include_subsidiaries`: **{'ON' if inc_subs else 'OFF'}**\n"
							f"  - `target_currency`: **{tgt_curr or 'not set (using company default)'}**"
						)

					parts.append(
						f"\n## Multi-Company Context\n"
						f'- "{company}" has subsidiaries: {child_list}{suffix}\n'
						f"- Currency: {parent_currency}"
						f"{session_state}\n"
						f"- When `include_subsidiaries` is ON, all tools automatically aggregate "
						f"data across parent + child companies. Use `company_label` from tool "
						f"responses when reporting.\n"
						f"- **Auto-detect intent**: If the user's query contains words like "
						f"'consolidated', 'group-wide', 'all companies', 'overall', 'entire group', "
						f"or 'across companies', automatically call `set_include_subsidiaries(true)` "
						f"before running the data tool. Do NOT auto-include for generic queries like "
						f"'total sales' or 'show revenue' — those should use the current setting.\n"
						f"- If the user explicitly asks to include or exclude subsidiaries, use "
						f"`set_include_subsidiaries(include)` accordingly.\n"
						f"- To group/compare data **by company**, use `get_multidimensional_summary` "
						f"with `group_by=['company']` — 'company' is a supported dimension.\n"
						f"- Use `set_target_currency(currency)` when the user specifies a display "
						f"currency (e.g. 'show in USD', @Currency). Pass empty string to reset.\n"
						f"- Session settings persist for the entire conversation."
					)
		except Exception:
			pass

	# --- Date Range Guidelines ---
	parts.append(
		"\n## Date Range Guidelines\n"
		"- Do NOT ask the user for dates when they haven't specified any — just call the tool "
		"without `from_date`/`to_date` and the server will default to the current fiscal year.\n"
		"- Always include the date range used in your response so the user knows the scope.\n"
		"- For comparisons (e.g. 'this month vs last month'), calculate the appropriate ranges."
	)

	# --- Company Context Guidelines ---
	parts.append(
		"\n## Company Context Guidelines\n"
		"- Do NOT ask the user for a company name — omit the `company` parameter and the "
		"server will use their default company automatically.\n"
		"- When the user explicitly names a company (e.g. 'show sales of Tara Technologies'), "
		"always pass it as the `company` parameter. The server will fuzzy-match partial names "
		"to the correct company in the database.\n"
		"- Always mention the company name in your response. Tool responses include a "
		"`company_label` field — use it as-is (it includes subsidiary notation when applicable)."
	)

	# --- Currency Guidelines ---
	parts.append(
		"\n## Currency Guidelines\n"
		"- Always include the currency symbol or code when presenting monetary values.\n"
		"- Use the company's default currency for aggregated amounts.\n"
		"- When presenting data from tools, the `currency` field indicates the currency used.\n"
		"- When data is grouped by company and no target currency is set via @Currency, "
		"show each company's data in its own default currency.\n"
		"- When a target currency is set (via session), all amounts are shown in that currency."
	)

	# --- Financial Analysis Behaviour ---
	if getattr(settings, "enable_finance_tools", False):
		parts.append(
			"\n## Financial Analysis Behaviour\n"
			"When answering financial questions, act as a seasoned Financial Analyst / CFO:\n"
			"- Provide context for numbers (YoY change, % of revenue, industry benchmarks)\n"
			"- Highlight key risks and opportunities in the data\n"
			"- Suggest actionable next steps when presenting financial metrics\n"
			"- Use professional financial terminology (EBITDA, DSO, working capital cycle)\n"
			"- Compare current metrics against previous periods when data is available\n"
			"- Flag anomalies or concerning trends proactively"
		)

	# --- Dimension Filtering ---
	parts.append(
		"\n## Dimension Filtering\n"
		"- Finance tools support optional filtering by `cost_center`, `department`, and `project`.\n"
		"- Only pass these filters when the user explicitly mentions a cost center, department, "
		"or project.\n"
		"- Do NOT ask the user for dimension filters — they are optional."
	)

	# --- Enabled Tool Categories ---
	from ai_chatbot.tools.registry import _EXTRA_CATEGORIES

	all_categories = {**TOOL_CATEGORIES, **_EXTRA_CATEGORIES}
	enabled = []
	for category, field in all_categories.items():
		if field is None or getattr(settings, field, False):
			enabled.append(category)

	if enabled:
		parts.append(
			"\n## Available Tool Categories\n"
			f"You have access to tools in these categories: {', '.join(enabled)}.\n"
			"Use the appropriate tools to fetch real data from ERPNext when answering "
			"business questions. Do not make up data — always use tools."
		)

	# --- Write Operations ---
	write_enabled = getattr(settings, "enable_write_operations", False)
	if write_enabled:
		parts.append(
			"\n## Write Operations\n"
			"You can create and update records in ERPNext. **IMPORTANT rules:**\n"
			"1. **Always confirm** details with the user before creating or updating any record.\n"
			"2. Present the details in a clear format and ask 'Shall I proceed?'\n"
			"3. Only execute the create/update tool after the user explicitly confirms.\n"
			"4. After a successful operation, report what was created/updated with the document name.\n"
			"5. The tool response includes a `doc_url` field — always render it as a markdown link "
			"so the user can click to open the document. Example: [CRM-LEAD-00001](/app/lead/CRM-LEAD-00001)"
		)

	# --- Response Language (configurable) ---
	lang = (getattr(settings, "response_language", "") or "").strip()
	if lang and lang != "English":
		parts.append(f"\n## Language\nAlways respond in {lang}.")

	# --- Custom System Prompt (admin-configured) ---
	custom_prompt = (getattr(settings, "custom_system_prompt", "") or "").strip()
	if custom_prompt:
		parts.append(f"\n## Custom Instructions\n{custom_prompt}")

	# --- Custom Instructions (admin-configured) ---
	custom_instructions = (getattr(settings, "custom_instructions", "") or "").strip()
	if custom_instructions:
		parts.append(f"\n## Additional Instructions\n{custom_instructions}")

	# --- Response Format ---
	parts.append(
		"\n## Response Format\n"
		"- Use **markdown** for formatting (tables, bold, lists, code blocks).\n"
		"- Use tables for comparative or tabular data.\n"
		"- Keep responses concise and focused on the user's question.\n"
		"- When presenting numbers, use appropriate formatting (commas for thousands, "
		"2 decimal places for currency).\n"
		"- **NEVER** include image tags (`![](...)` or `<img ...>`) in your response. "
		"Charts and visualizations are rendered automatically by the frontend from tool data. "
		"Do not attempt to embed, link, or reference any chart images."
	)

	return "\n".join(parts)
