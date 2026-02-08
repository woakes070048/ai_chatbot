"""
Base Tool Module
Base classes and utilities for ERPNext tools
"""

import frappe
from typing import Dict, List, Any


class BaseTool:
	"""Base class for all ERPNext tools"""
	
	@staticmethod
	def get_tools_schema() -> List[Dict]:
		"""
		Get OpenAI function calling schema for tools
		Should be implemented by child classes
		"""
		raise NotImplementedError
	
	@staticmethod
	def execute_tool(tool_name: str, arguments: Dict) -> Dict:
		"""Execute a tool and return results"""
		try:
			# Import the tool function dynamically
			from ai_chatbot.tools.crm import CRMTools
			from ai_chatbot.tools.buying import BuyingTools
			from ai_chatbot.tools.selling import SellingTools
			from ai_chatbot.tools.stock import StockTools
			from ai_chatbot.tools.account import AccountTools
			from ai_chatbot.tools.hrms import HRMSTools
			
			# Try to find the function
			method = None
			for tool_class in [CRMTools, BuyingTools, SellingTools, StockTools, AccountTools, HRMSTools]:
				if hasattr(tool_class, tool_name):
					method = getattr(tool_class, tool_name)
					break
			
			if method:
				result = method(**arguments)
				return {"success": True, "data": result}
			else:
				return {"success": False, "error": f"Tool {tool_name} not found"}
				
		except Exception as e:
			frappe.log_error(f"Tool execution error: {str(e)}", "Chatbot Tools")
			return {"success": False, "error": str(e)}


def get_all_tools_schema() -> List[Dict]:
	"""Get combined schema from all tool modules"""
	from ai_chatbot.tools.crm import CRMTools
	from ai_chatbot.tools.buying import BuyingTools
	from ai_chatbot.tools.selling import SellingTools
	from ai_chatbot.tools.stock import StockTools
	from ai_chatbot.tools.account import AccountTools
	
	settings = frappe.get_single("Chatbot Settings")
	
	tools = []
	
	if settings.enable_crm_tools:
		tools.extend(CRMTools.get_tools_schema())
	
	if settings.enable_sales_tools:
		tools.extend(SellingTools.get_tools_schema())
	
	if settings.enable_purchase_tools:
		tools.extend(BuyingTools.get_tools_schema())
	
	if settings.enable_finance_tools:
		tools.extend(AccountTools.get_tools_schema())
	
	if settings.enable_inventory_tools:
		tools.extend(StockTools.get_tools_schema())
	
	return tools
