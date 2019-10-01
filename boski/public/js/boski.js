
/*
	Developer Sahil Saini
 	Email sahil.saini@grynn.in
 */

frappe.provide("boski");

frappe.provide('erpnext');

// add toolbar icon
$(document).bind('toolbar_setup', function() {
	frappe.app.name = "ERPNext";

	var $help_menu = $('.dropdown-help ul .documentation-links');
	$('<li><a data-link-type="forum" href="docs/user/manual" \ target="_blank">'+__('Documentation')+'</a></li>').insertBefore($help_menu);
});
