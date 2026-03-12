# Copyright (c) 2026, Sanjay Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChatbotScheduledReport(Document):
	"""Chatbot Scheduled Report — scheduled AI-generated reports.

	Validates schedule configuration and ensures consistency between
	the schedule type and its dependent fields.
	"""

	def validate(self):
		"""Validate schedule configuration."""
		self._validate_schedule_fields()
		self._validate_recipients()

	@frappe.whitelist()
	def run_now(self):
		"""Manually trigger this report immediately via background job."""
		if not self.enabled:
			frappe.throw("Cannot run a disabled report. Please enable it first.")

		frappe.enqueue(
			"ai_chatbot.automation.scheduled_reports._execute_single_report",
			queue="long",
			timeout=600,
			now=False,
			report_name=self.name,
		)

		frappe.msgprint(
			f"Report <b>{self.report_name}</b> has been queued for execution. "
			"Check the Status tab for results.",
			title="Report Queued",
			indicator="blue",
		)

	def _validate_schedule_fields(self):
		"""Ensure schedule-dependent fields are set correctly."""
		if self.schedule == "Weekly" and not self.day_of_week:
			frappe.throw("Day of Week is required for weekly schedule.")

		if self.schedule == "Monthly":
			if not self.day_of_month:
				frappe.throw("Day of Month is required for monthly schedule.")
			if self.day_of_month < 1 or self.day_of_month > 28:
				frappe.throw("Day of Month must be between 1 and 28.")

		if self.schedule == "Custom Cron":
			if not self.cron_expression:
				frappe.throw("Cron Expression is required for custom cron schedule.")
			self._validate_cron_expression()

	def _validate_cron_expression(self):
		"""Validate cron expression syntax."""
		try:
			from croniter import croniter

			croniter(self.cron_expression)
		except (ValueError, KeyError) as e:
			frappe.throw(f"Invalid cron expression: {self.cron_expression} — {e!s}")
		except ImportError:
			# croniter not available — skip validation
			pass

	def _validate_recipients(self):
		"""Ensure at least one recipient is configured."""
		if not self.recipients or len(self.recipients) == 0:
			frappe.throw("At least one recipient is required.")
