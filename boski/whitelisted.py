# run boski manager #

import frappe
from boski.utils.boski import boski_manager
from frappe import _, msgprint

def after_submit(doc, method):
        try:
                doctype = doc.meta.get("name")
                print("sahil is here", doctype, method, doc.name, doc.party)
                frappe.msgprint(_("Thanks For choosing GRYNN. We are working for you. We will notify you with email once your site is ready."))
                boski_manager(doc.party, "guest", allow_guest=True)
        except Exception as e:
                frappe.msgprint(e)
