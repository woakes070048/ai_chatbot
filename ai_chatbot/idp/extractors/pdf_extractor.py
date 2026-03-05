# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
"""
PDF text extraction using pypdf.

Extracts selectable text from all pages of a PDF document.
If the PDF is scanned (image-only), returns empty string —
the caller falls back to Vision API via base64 image.
"""

from __future__ import annotations

import io


def extract_pdf_text(file_bytes: bytes) -> str:
	"""Extract text from a PDF file.

	Args:
		file_bytes: Raw PDF file content.

	Returns:
		Concatenated text from all pages, separated by newlines.
		Empty string if no selectable text found (scanned PDF).
	"""
	try:
		from pypdf import PdfReader
	except ImportError:
		import frappe

		frappe.throw("pypdf is required for PDF text extraction. Install it with: pip install pypdf")

	reader = PdfReader(io.BytesIO(file_bytes))
	pages = []
	for page in reader.pages:
		text = page.extract_text()
		if text:
			pages.append(text.strip())

	return "\n\n".join(pages)
