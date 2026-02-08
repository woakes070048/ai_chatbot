// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on('Chatbot Settings', {
	refresh: function(frm) {
		// Add custom buttons or UI logic here
		frm.add_custom_button(__('Test OpenAI Connection'), function() {
			test_openai_connection(frm);
		});
		
		frm.add_custom_button(__('Test Claude Connection'), function() {
			test_claude_connection(frm);
		});
	},
	
	openai_enabled: function(frm) {
		// Toggle visibility of OpenAI fields
		frm.toggle_display(['openai_api_key', 'openai_model', 'openai_temperature', 'openai_max_tokens'], frm.doc.openai_enabled);
	},
	
	claude_enabled: function(frm) {
		// Toggle visibility of Claude fields
		frm.toggle_display(['claude_api_key', 'claude_model', 'claude_temperature', 'claude_max_tokens'], frm.doc.claude_enabled);
	}
});

function test_openai_connection(frm) {
	if (!frm.doc.openai_enabled) {
		frappe.msgprint(__('OpenAI is not enabled'));
		return;
	}
	
	if (!frm.doc.openai_api_key) {
		frappe.msgprint(__('Please enter OpenAI API Key'));
		return;
	}
	
	frappe.show_alert({
		message: __('Testing OpenAI connection...'),
		indicator: 'blue'
	});
	
	// Call server method to test connection
	frappe.call({
		method: 'ai_chatbot.utils.ai_providers.test_openai_connection',
		args: {
			api_key: frm.doc.openai_api_key,
			model: frm.doc.openai_model
		},
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({
					message: __('OpenAI connection successful!'),
					indicator: 'green'
				});
			} else {
				frappe.show_alert({
					message: __('OpenAI connection failed: ') + (r.message ? r.message.error : 'Unknown error'),
					indicator: 'red'
				});
			}
		}
	});
}

function test_claude_connection(frm) {
	if (!frm.doc.claude_enabled) {
		frappe.msgprint(__('Claude is not enabled'));
		return;
	}
	
	if (!frm.doc.claude_api_key) {
		frappe.msgprint(__('Please enter Claude API Key'));
		return;
	}
	
	frappe.show_alert({
		message: __('Testing Claude connection...'),
		indicator: 'blue'
	});
	
	// Call server method to test connection
	frappe.call({
		method: 'ai_chatbot.utils.ai_providers.test_claude_connection',
		args: {
			api_key: frm.doc.claude_api_key,
			model: frm.doc.claude_model
		},
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({
					message: __('Claude connection successful!'),
					indicator: 'green'
				});
			} else {
				frappe.show_alert({
					message: __('Claude connection failed: ') + (r.message ? r.message.error : 'Unknown error'),
					indicator: 'red'
				});
			}
		}
	});
}
