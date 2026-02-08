"""
Account Tools Module
Finance and accounting tools for AI Chatbot
"""

import frappe
from frappe.utils import flt, nowdate, add_days
from typing import Dict, List


class AccountTools:
	"""Finance related tools"""
	
	@staticmethod
	def get_tools_schema() -> List[Dict]:
		"""Get account tools schema"""
		return [
			{
				"type": "function",
				"function": {
					"name": "get_financial_summary",
					"description": "Get financial summary including P&L, balance sheet highlights",
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
					"name": "get_cash_flow_analysis",
					"description": "Analyze cash flow patterns and trends",
					"parameters": {
						"type": "object",
						"properties": {
							"months": {"type": "integer", "description": "Number of months to analyze", "default": 6}
						}
					}
				}
			}
		]
	
	@staticmethod
	def get_financial_summary(from_date=None, to_date=None):
		"""Get financial summary"""
		if not from_date:
			from_date = add_days(nowdate(), -30)
		if not to_date:
			to_date = nowdate()
		
		# Revenue
		revenue = frappe.db.sql("""
			SELECT SUM(grand_total) as total
			FROM `tabSales Invoice`
			WHERE docstatus = 1
			AND posting_date BETWEEN %s AND %s
		""", (from_date, to_date), as_dict=True)[0].total or 0
		
		# Expenses
		expenses = frappe.db.sql("""
			SELECT SUM(grand_total) as total
			FROM `tabPurchase Invoice`
			WHERE docstatus = 1
			AND posting_date BETWEEN %s AND %s
		""", (from_date, to_date), as_dict=True)[0].total or 0
		
		return {
			"revenue": flt(revenue),
			"expenses": flt(expenses),
			"profit": flt(revenue) - flt(expenses),
			"period": {"from": from_date, "to": to_date}
		}
	
	@staticmethod
	def get_cash_flow_analysis(months=6):
		"""Get cash flow analysis"""
		end_date = nowdate()
		start_date = add_days(end_date, -months * 30)
		
		# Simplified cash flow
		inflow = frappe.db.sql("""
			SELECT SUM(paid_amount) as total
			FROM `tabPayment Entry`
			WHERE docstatus = 1
			AND payment_type = 'Receive'
			AND posting_date BETWEEN %s AND %s
		""", (start_date, end_date), as_dict=True)[0].total or 0
		
		outflow = frappe.db.sql("""
			SELECT SUM(paid_amount) as total
			FROM `tabPayment Entry`
			WHERE docstatus = 1
			AND payment_type = 'Pay'
			AND posting_date BETWEEN %s AND %s
		""", (start_date, end_date), as_dict=True)[0].total or 0
		
		return {
			"cash_inflow": flt(inflow),
			"cash_outflow": flt(outflow),
			"net_cash_flow": flt(inflow) - flt(outflow),
			"period_months": months
		}
