"""
CRM Tools Module
Customer Relationship Management tools for AI Chatbot
"""

import frappe
from frappe.utils import flt, getdate
from typing import Dict, List


class CRMTools:
	"""CRM related tools"""
	
	@staticmethod
	def get_tools_schema() -> List[Dict]:
		"""Get CRM tools schema"""
		return [
			{
				"type": "function",
				"function": {
					"name": "get_lead_statistics",
					"description": "Get statistics about leads including count, status breakdown, and conversion rates",
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
					"name": "get_opportunity_pipeline",
					"description": "Get sales opportunity pipeline with stages and values",
					"parameters": {
						"type": "object",
						"properties": {
							"status": {"type": "string", "description": "Filter by status (Open, Converted, Lost)"}
						}
					}
				}
			}
		]
	
	@staticmethod
	def get_lead_statistics(from_date=None, to_date=None):
		"""Get lead statistics"""
		filters = {}
		if from_date:
			filters["creation"] = [">=", from_date]
		if to_date:
			filters["creation"] = ["<=", to_date]
		
		leads = frappe.get_all("Lead", filters=filters, fields=["status"])
		
		status_count = {}
		for lead in leads:
			status = lead.status
			status_count[status] = status_count.get(status, 0) + 1
		
		return {
			"total_leads": len(leads),
			"status_breakdown": status_count,
			"period": {"from": from_date, "to": to_date}
		}
	
	@staticmethod
	def get_opportunity_pipeline(status=None):
		"""Get opportunity pipeline"""
		filters = {}
		if status:
			filters["status"] = status
		
		opportunities = frappe.get_all(
			"Opportunity",
			filters=filters,
			fields=["name", "opportunity_amount", "status", "sales_stage", "customer_name"]
		)
		
		pipeline = {
			"opportunities": opportunities,
			"total_value": sum(flt(opp.get("opportunity_amount", 0)) for opp in opportunities),
			"count": len(opportunities)
		}
		
		return pipeline
