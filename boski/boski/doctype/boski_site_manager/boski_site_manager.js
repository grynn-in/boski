// Copyright (c) 2019, GRYNN and contributors
// For license information, please see license.txt

frappe.ui.form.on('Boski Site Manager', {
	// refresh: function(frm) {

	// }
});

frappe.provide("boski.boski_site_manager");

boski.boski_site_manager.BoskiSiteManager = Class.extend({
	init: function(args){
		$.extend(this, args);
	},

	refresh: function(){
		var me = this;
		me.frm.add_custom_button(__('Make Boski Site'), function(){
			frappe.msgprint("sahil is here");
		});
	}
});
cur_frm.script_manager.make(boski.boski_site_manager.BoskiSiteManager);
