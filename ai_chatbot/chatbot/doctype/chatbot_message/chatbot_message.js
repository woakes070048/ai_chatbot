// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on('Chatbot Message', {
	refresh: function(frm) {
		// Make certain fields read-only
		frm.set_df_property('timestamp', 'read_only', 1);
		frm.set_df_property('tokens_used', 'read_only', 1);
		
		// Add button to view conversation
		if (frm.doc.conversation) {
			frm.add_custom_button(__('View Conversation'), function() {
				frappe.set_route("Form", "Chatbot Conversation", frm.doc.conversation);
			});
		}
	}
});
