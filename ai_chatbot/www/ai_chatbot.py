# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt
import frappe


def get_context(context):
	"""Set context for AI Chatbot page"""
	context.no_cache = 1

	# Check if user is logged in
	if frappe.session.user == "Guest":
		frappe.throw("Please login to access AI Chatbot", frappe.PermissionError)

	# Pass site name to template (frappe.local is not directly accessible in Jinja2)
	context.site_name = frappe.local.site

	return context
