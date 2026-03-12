// Copyright (c) 2026, Sanjay Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Chatbot Scheduled Report", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Run Now"), function () {
				frappe.confirm(
					__("This will execute the report immediately and email the results. Continue?"),
					function () {
						frm.call("run_now").then(() => {
							frm.reload_doc();
						});
					}
				);
			});
		}
	},
});
