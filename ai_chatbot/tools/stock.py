"""
Stock Tools Module
Inventory and warehouse management tools for AI Chatbot
"""

import frappe
from frappe.utils import flt
from typing import Dict, List


class StockTools:
	"""Inventory related tools"""
	
	@staticmethod
	def get_tools_schema() -> List[Dict]:
		"""Get stock tools schema"""
		return [
			{
				"type": "function",
				"function": {
					"name": "get_inventory_summary",
					"description": "Get inventory summary including stock levels, valuation",
					"parameters": {
						"type": "object",
						"properties": {
							"warehouse": {"type": "string", "description": "Filter by warehouse"}
						}
					}
				}
			},
			{
				"type": "function",
				"function": {
					"name": "get_low_stock_items",
					"description": "Get items with low stock levels",
					"parameters": {
						"type": "object",
						"properties": {
							"threshold_days": {"type": "integer", "description": "Days of stock threshold", "default": 30}
						}
					}
				}
			}
		]
	
	@staticmethod
	def get_inventory_summary(warehouse=None):
		"""Get inventory summary"""
		filters = {}
		if warehouse:
			filters["warehouse"] = warehouse
		
		stock = frappe.db.sql("""
			SELECT 
				COUNT(DISTINCT item_code) as item_count,
				SUM(actual_qty) as total_qty,
				SUM(stock_value) as total_value
			FROM `tabBin`
			{where_clause}
		""".format(
			where_clause=f"WHERE warehouse = '{warehouse}'" if warehouse else ""
		), as_dict=True)[0]
		
		return {
			"unique_items": stock.item_count or 0,
			"total_quantity": flt(stock.total_qty or 0),
			"total_value": flt(stock.total_value or 0),
			"warehouse": warehouse
		}
	
	@staticmethod
	def get_low_stock_items(threshold_days=30):
		"""Get low stock items"""
		# Simplified - items with qty less than reorder level
		items = frappe.db.sql("""
			SELECT 
				b.item_code,
				b.actual_qty,
				i.item_name,
				ir.warehouse_reorder_level
			FROM `tabBin` b
			INNER JOIN `tabItem` i ON b.item_code = i.name
			LEFT JOIN `tabItem Reorder` ir ON b.item_code = ir.parent
			WHERE b.actual_qty < COALESCE(ir.warehouse_reorder_level, 10)
			ORDER BY b.actual_qty ASC
			LIMIT 50
		""", as_dict=True)
		
		return {
			"low_stock_items": items,
			"count": len(items)
		}
