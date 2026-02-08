"""
Buying Tools Module
Purchase and supplier management tools for AI Chatbot
"""

import frappe
from frappe.utils import flt
from typing import Dict, List


class BuyingTools:
	"""Purchase related tools"""
	
	@staticmethod
	def get_tools_schema() -> List[Dict]:
		"""Get buying tools schema"""
		return [
			{
				"type": "function",
				"function": {
					"name": "get_purchase_analytics",
					"description": "Get purchase analytics including spending, orders, and supplier performance",
					"parameters": {
						"type": "object",
						"properties": {
							"from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
							"to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
						}
					}
				}
			},
			{
				"type": "function",
				"function": {
					"name": "get_supplier_performance",
					"description": "Analyze supplier performance metrics",
					"parameters": {
						"type": "object",
						"properties": {
							"supplier": {"type": "string", "description": "Supplier name"}
						}
					}
				}
			}
		]
	
	@staticmethod
	def get_purchase_analytics(from_date=None, to_date=None):
		"""Get purchase analytics"""
		filters = {"docstatus": 1}
		if from_date:
			filters["posting_date"] = [">=", from_date]
		if to_date:
			filters["posting_date"] = ["<=", to_date]
		
		invoices = frappe.get_all(
			"Purchase Invoice",
			filters=filters,
			fields=["grand_total", "posting_date", "supplier"]
		)
		
		total_spending = sum(flt(inv.grand_total) for inv in invoices)
		
		return {
			"total_spending": total_spending,
			"invoice_count": len(invoices),
			"average_order_value": total_spending / len(invoices) if invoices else 0,
			"period": {"from": from_date, "to": to_date}
		}
	
	@staticmethod
	def get_supplier_performance(supplier=None):
		"""Get supplier performance metrics"""
		filters = {"docstatus": 1}
		if supplier:
			filters["supplier"] = supplier
		
		purchases = frappe.get_all(
			"Purchase Order",
			filters=filters,
			fields=["supplier", "grand_total", "status", "transaction_date"]
		)
		
		return {
			"total_orders": len(purchases),
			"total_value": sum(flt(p.grand_total) for p in purchases),
			"supplier": supplier
		}
