"""
Selling Tools Module
Sales and customer analytics tools for AI Chatbot
"""

import frappe
from frappe.utils import flt
from typing import Dict, List


class SellingTools:
	"""Sales related tools"""
	
	@staticmethod
	def get_tools_schema() -> List[Dict]:
		"""Get selling tools schema"""
		return [
			{
				"type": "function",
				"function": {
					"name": "get_sales_analytics",
					"description": "Get sales analytics including revenue, orders, and growth trends",
					"parameters": {
						"type": "object",
						"properties": {
							"from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
							"to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
							"customer": {"type": "string", "description": "Filter by customer name"}
						}
					}
				}
			},
			{
				"type": "function",
				"function": {
					"name": "get_top_customers",
					"description": "Get top customers by revenue",
					"parameters": {
						"type": "object",
						"properties": {
							"limit": {"type": "integer", "description": "Number of customers to return", "default": 10},
							"from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"}
						}
					}
				}
			}
		]
	
	@staticmethod
	def get_sales_analytics(from_date=None, to_date=None, customer=None):
		"""Get sales analytics"""
		filters = {"docstatus": 1}
		if from_date:
			filters["posting_date"] = [">=", from_date]
		if to_date:
			filters["posting_date"] = ["<=", to_date]
		if customer:
			filters["customer"] = customer
		
		invoices = frappe.get_all(
			"Sales Invoice",
			filters=filters,
			fields=["grand_total", "posting_date", "customer"]
		)
		
		total_revenue = sum(flt(inv.grand_total) for inv in invoices)
		
		return {
			"total_revenue": total_revenue,
			"invoice_count": len(invoices),
			"average_order_value": total_revenue / len(invoices) if invoices else 0,
			"period": {"from": from_date, "to": to_date}
		}
	
	@staticmethod
	def get_top_customers(limit=10, from_date=None):
		"""Get top customers by revenue"""
		filters = {"docstatus": 1}
		if from_date:
			filters["posting_date"] = [">=", from_date]
		
		customers = frappe.db.sql("""
			SELECT 
				customer,
				SUM(grand_total) as total_revenue,
				COUNT(*) as order_count
			FROM `tabSales Invoice`
			WHERE docstatus = 1
			{date_filter}
			GROUP BY customer
			ORDER BY total_revenue DESC
			LIMIT {limit}
		""".format(
			date_filter=f"AND posting_date >= '{from_date}'" if from_date else "",
			limit=limit
		), as_dict=True)
		
		return {"top_customers": customers}
