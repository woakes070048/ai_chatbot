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


def build_system_prompt():
	"""Build the system prompt with dynamic context.

	Includes:
	- ERPNext assistant persona (configurable)
	- Current user name, company, currency, fiscal year dates
	- Guidelines for default date ranges and currency handling
	- Enabled tool categories
	- Accounting dimension filtering context
	- Multi-company consolidation context (if parent company)
	- Write operation confirmation rules (if enabled)
	- Response language (configurable)
	- Custom system prompt and instructions (configurable)
	- Response format guidelines

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

	# --- Multi-Company Consolidation Context ---
	if company:
		try:
			from ai_chatbot.core.consolidation import get_child_companies, is_parent_company

			if is_parent_company(company):
				children = get_child_companies(company)
				if children:
					child_list = ", ".join(children[:10])
					suffix = f" (and {len(children) - 10} more)" if len(children) > 10 else ""
					parent_currency = get_company_currency(company)
					parts.append(
						f"\n## Multi-Company Context\n"
						f'- Your company "{company}" is a parent company with subsidiaries: '
						f"{child_list}{suffix}\n"
						f"- When the user asks for consolidated/group/total data across companies, "
						f"ask them:\n"
						f"  1. Whether to include child companies in the report\n"
						f"  2. Which currency to display results in "
						f"(default: {parent_currency})\n"
						f"- After the user confirms, use the `get_consolidated_report` tool with "
						f"the appropriate tool name and parameters.\n"
						f"- When filtering by a specific subsidiary, pass that company name "
						f"explicitly to the individual tool instead."
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
		"- Only pass `company` when the user explicitly names a different company."
	)

	# --- Currency Guidelines ---
	parts.append(
		"\n## Currency Guidelines\n"
		"- Always include the currency symbol or code when presenting monetary values.\n"
		"- Use the company's default currency for aggregated amounts.\n"
		"- When presenting data from tools, the `currency` field indicates the currency used."
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
