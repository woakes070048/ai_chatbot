# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
Document vs ERPNext Record Comparison

Compares extracted document data with an existing ERPNext record and
generates a field-by-field discrepancy report.

Use case: User uploads a client's Purchase Order PDF and compares it
against an existing Sales Order to find differences.
"""

from __future__ import annotations

import frappe
from frappe.utils import flt, getdate

from ai_chatbot.idp.schema import get_doctype_schema


def compare_with_record(
	extracted_data: dict,
	doctype: str,
	docname: str,
) -> dict:
	"""Compare extracted document data with an existing ERPNext record.

	Performs a field-by-field comparison for header fields and line items.

	Args:
		extracted_data: Mapped data from IDP extraction.
		doctype: ERPNext DocType name.
		docname: Document name to compare against.

	Returns:
		dict:
			matches: list of {field, label, value} — fields that match
			discrepancies: list of {field, label, extracted, existing} — fields that differ
			missing_in_document: list — fields in record but not in extracted data
			missing_in_record: list — fields in extracted data but not in record
			items_comparison: list — per-item comparison results
			summary: str — human-readable summary
	"""
	if not frappe.db.exists(doctype, docname):
		return {"error": f"{doctype} '{docname}' does not exist"}

	doc = frappe.get_doc(doctype, docname)
	schema = get_doctype_schema(doctype)

	matches = []
	discrepancies = []
	missing_in_document = []
	missing_in_record = []

	# Compare header fields
	for field in schema.get("fields", []):
		fieldname = field["fieldname"]
		label = field["label"]
		ftype = field["fieldtype"]

		extracted_val = extracted_data.get(fieldname)
		record_val = doc.get(fieldname)

		if extracted_val is None and record_val is None:
			continue

		if extracted_val is None and record_val is not None:
			missing_in_document.append({"field": fieldname, "label": label, "existing": record_val})
			continue

		if extracted_val is not None and record_val is None:
			missing_in_record.append({"field": fieldname, "label": label, "extracted": extracted_val})
			continue

		is_match = _values_match(extracted_val, record_val, ftype)
		if is_match:
			matches.append({"field": fieldname, "label": label, "value": record_val})
		else:
			discrepancies.append(
				{
					"field": fieldname,
					"label": label,
					"extracted": extracted_val,
					"existing": record_val,
				}
			)

	# Compare items (child table)
	items_comparison = _compare_items(extracted_data, doc, schema)

	# Build summary
	total_compared = len(matches) + len(discrepancies)
	summary = (
		f"{len(matches)} of {total_compared} header fields match. {len(discrepancies)} discrepancies found."
	)
	if items_comparison.get("item_discrepancies"):
		summary += f" {len(items_comparison['item_discrepancies'])} item-level differences."

	return {
		"matches": matches,
		"discrepancies": discrepancies,
		"missing_in_document": missing_in_document,
		"missing_in_record": missing_in_record,
		"items_comparison": items_comparison,
		"summary": summary,
	}


def _values_match(extracted, existing, field_type: str) -> bool:
	"""Compare two values with type-aware comparison.

	Args:
		extracted: Value from document extraction.
		existing: Value from ERPNext record.
		field_type: ERPNext field type.

	Returns:
		True if values are semantically equivalent.
	"""
	if field_type in ("Date", "Datetime"):
		try:
			return getdate(str(extracted)) == getdate(str(existing))
		except Exception:
			return str(extracted).strip() == str(existing).strip()

	if field_type in ("Currency", "Float", "Percent"):
		try:
			return flt(extracted, 2) == flt(existing, 2)
		except Exception:
			return str(extracted).strip() == str(existing).strip()

	if field_type == "Int":
		try:
			return int(float(str(extracted))) == int(float(str(existing)))
		except Exception:
			return str(extracted).strip() == str(existing).strip()

	# String comparison — case-insensitive, whitespace-trimmed
	return str(extracted).strip().lower() == str(existing).strip().lower()


def _compare_items(
	extracted_data: dict,
	doc,
	schema: dict,
) -> dict:
	"""Compare extracted line items with existing document items.

	Uses a best-effort matching strategy:
	1. Match by item_code if available
	2. Match by position (index) as fallback

	Args:
		extracted_data: Extracted data with items array.
		doc: Frappe document object.
		schema: DocType schema.

	Returns:
		dict with item_matches, item_discrepancies, and summary.
	"""
	# Find the items child table
	items_fieldname = None
	child_schema = None
	for table_name, child in schema.get("child_tables", {}).items():
		items_fieldname = table_name
		child_schema = child
		break

	if not items_fieldname or not child_schema:
		return {"item_matches": [], "item_discrepancies": [], "extra_extracted": [], "extra_existing": []}

	extracted_items = extracted_data.get(items_fieldname, [])
	if not isinstance(extracted_items, list):
		extracted_items = []

	existing_items = doc.get(items_fieldname, [])

	item_matches = []
	item_discrepancies = []

	# Build index of existing items by item_code for matching
	existing_by_code = {}
	for idx, eitem in enumerate(existing_items):
		code = getattr(eitem, "item_code", None)
		if code:
			existing_by_code[code] = (idx, eitem)

	matched_existing_indices = set()

	for ext_idx, ext_item in enumerate(extracted_items):
		ext_code = ext_item.get("item_code", "")
		matched_existing = None
		matched_idx = None

		# Try matching by item_code
		if ext_code and ext_code in existing_by_code:
			matched_idx, matched_existing = existing_by_code[ext_code]
		# Fallback: match by position
		elif ext_idx < len(existing_items):
			matched_idx = ext_idx
			matched_existing = existing_items[ext_idx]

		if matched_existing is None:
			item_discrepancies.append(
				{
					"row": ext_idx + 1,
					"type": "extra_in_document",
					"item": ext_item,
				}
			)
			continue

		matched_existing_indices.add(matched_idx)

		# Compare fields for this item pair
		row_diffs = []
		for cf in child_schema.get("fields", []):
			cfname = cf["fieldname"]
			ext_val = ext_item.get(cfname)
			exist_val = getattr(matched_existing, cfname, None)

			if ext_val is None or exist_val is None:
				continue

			if not _values_match(ext_val, exist_val, cf["fieldtype"]):
				row_diffs.append(
					{
						"field": cfname,
						"label": cf["label"],
						"extracted": ext_val,
						"existing": exist_val,
					}
				)

		if row_diffs:
			item_discrepancies.append(
				{
					"row": ext_idx + 1,
					"item_code": ext_code,
					"type": "field_mismatch",
					"differences": row_diffs,
				}
			)
		else:
			item_matches.append(
				{
					"row": ext_idx + 1,
					"item_code": ext_code or f"Row {ext_idx + 1}",
				}
			)

	# Items in existing record but not in extracted data
	extra_existing = []
	for idx, eitem in enumerate(existing_items):
		if idx not in matched_existing_indices:
			extra_existing.append(
				{
					"row": idx + 1,
					"item_code": getattr(eitem, "item_code", ""),
					"type": "extra_in_record",
				}
			)

	return {
		"item_matches": item_matches,
		"item_discrepancies": item_discrepancies,
		"extra_existing": extra_existing,
	}
