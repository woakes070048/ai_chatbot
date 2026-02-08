// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on('Chatbot Conversation', {
	refresh: function(frm) {
		// Add custom button to view messages
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Messages'), function() {
				frappe.route_options = {"conversation": frm.doc.name};
				frappe.set_route("List", "Chatbot Message");
			});
			
			// Add button to open chatbot
			frm.add_custom_button(__('Open Chatbot'), function() {
				window.open('/ai-chatbot?conversation=' + frm.doc.name, '_blank');
			}, __('Actions'));
		}
		
		// Make certain fields read-only
		frm.set_df_property('message_count', 'read_only', 1);
		frm.set_df_property('total_tokens', 'read_only', 1);
		frm.set_df_property('created_at', 'read_only', 1);
		frm.set_df_property('updated_at', 'read_only', 1);
	}
});
