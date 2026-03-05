# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
ERPNext DocType Schema Discovery

Dynamically reads DocType field definitions using frappe.get_meta()
to build a schema description that the LLM uses for semantic mapping.
"""

from __future__ import annotations

import frappe

# Field types relevant for document extraction
# Excludes layout fields (Section Break, Column Break, Tab Break, etc.)
EXTRACTABLE_FIELD_TYPES = {
	"Data",
	"Link",
	"Date",
	"Datetime",
	"Currency",
	"Float",
	"Int",
	"Select",
	"Text",
	"Small Text",
	"Long Text",
	"Text Editor",
	"Check",
	"Percent",
	"Rating",
	"Duration",
	"Dynamic Link",
	"Table",
}

# DocTypes commonly used as IDP targets
SUPPORTED_DOCTYPES = {
	"Sales Invoice",
	"Purchase Invoice",
	"Quotation",
	"Sales Order",
	"Purchase Order",
	"Delivery Note",
	"Purchase Receipt",
}


def get_doctype_schema(doctype: str) -> dict:
	"""Get field definitions for an ERPNext DocType.

	Reads the DocType meta to discover fields, their types, labels,
	link targets, and whether they are required. Also discovers child
	tables (e.g., items table) and their field schemas.

	Args:
		doctype: DocType name (e.g., "Sales Invoice").

	Returns:
		dict:
			doctype: str — the DocType name
			fields: list[dict] — field definitions (fieldname, label, fieldtype, options, reqd)
			child_tables: dict — {fieldname: {doctype, parentfield, fields: [...]}}
	"""
	meta = frappe.get_meta(doctype)
	fields = []
	child_tables = {}

	for df in meta.fields:
		if df.fieldtype not in EXTRACTABLE_FIELD_TYPES:
			continue

		if df.fieldtype == "Table":
			# Discover child table schema
			child_doctype = df.options
			if child_doctype:
				child_tables[df.fieldname] = {
					"doctype": child_doctype,
					"parentfield": df.fieldname,
					"label": df.label or df.fieldname,
					"fields": _get_child_fields(child_doctype),
				}
			continue

		field_info = {
			"fieldname": df.fieldname,
			"label": df.label or df.fieldname,
			"fieldtype": df.fieldtype,
			"reqd": bool(df.reqd),
		}

		if df.options:
			if df.fieldtype == "Link":
				field_info["link_doctype"] = df.options
			elif df.fieldtype == "Select":
				field_info["options"] = df.options.split("\n")
			elif df.fieldtype == "Dynamic Link":
				field_info["link_depends_on"] = df.options

		if df.default:
			field_info["default"] = df.default

		fields.append(field_info)

	return {
		"doctype": doctype,
		"fields": fields,
		"child_tables": child_tables,
	}


def _get_child_fields(child_doctype: str) -> list[dict]:
	"""Get extractable field definitions for a child table DocType.

	Excludes standard parent linkage fields (parent, parentfield, parenttype, idx).

	Args:
		child_doctype: Child DocType name (e.g., "Sales Invoice Item").

	Returns:
		list of field definition dicts.
	"""
	meta = frappe.get_meta(child_doctype)
	skip_fields = {"parent", "parentfield", "parenttype", "idx", "name", "owner", "docstatus"}
	fields = []

	for df in meta.fields:
		if df.fieldtype not in EXTRACTABLE_FIELD_TYPES:
			continue
		if df.fieldname in skip_fields:
			continue
		# Skip nested child tables inside child tables
		if df.fieldtype == "Table":
			continue

		field_info = {
			"fieldname": df.fieldname,
			"label": df.label or df.fieldname,
			"fieldtype": df.fieldtype,
			"reqd": bool(df.reqd),
		}

		if df.options:
			if df.fieldtype == "Link":
				field_info["link_doctype"] = df.options
			elif df.fieldtype == "Select":
				field_info["options"] = df.options.split("\n")

		fields.append(field_info)

	return fields


def build_schema_prompt(doctype: str) -> str:
	"""Build a human-readable schema description for the LLM extraction prompt.

	Converts the DocType schema into a structured text that the LLM uses
	to understand what fields to extract and their expected formats.

	Args:
		doctype: DocType name.

	Returns:
		Multi-line string describing the target schema.
	"""
	schema = get_doctype_schema(doctype)
	lines = [f"Target DocType: {schema['doctype']}", "", "## Header Fields"]

	for f in schema["fields"]:
		required = " (REQUIRED)" if f.get("reqd") else ""
		ftype = f["fieldtype"]
		desc = f"- **{f['label']}** (`{f['fieldname']}`): {ftype}{required}"

		if f.get("link_doctype"):
			desc += f" → links to {f['link_doctype']}"
		if f.get("options") and isinstance(f["options"], list):
			opts = ", ".join(f["options"][:10])
			desc += f" — options: [{opts}]"
		if f.get("default"):
			desc += f" — default: {f['default']}"

		lines.append(desc)

	for field_name, child in schema.get("child_tables", {}).items():
		lines.append(f"\n## Child Table: {child['label']} (`{field_name}`)")
		lines.append(f"Child DocType: {child['doctype']}")
		for cf in child["fields"]:
			required = " (REQUIRED)" if cf.get("reqd") else ""
			ftype = cf["fieldtype"]
			desc = f"- **{cf['label']}** (`{cf['fieldname']}`): {ftype}{required}"
			if cf.get("link_doctype"):
				desc += f" → links to {cf['link_doctype']}"
			lines.append(desc)

	return "\n".join(lines)
