# run boski manager #

import frappe
from boski.utils.boski import boski_manager
from frappe import _, msgprint
from frappe.utils.background_jobs import enqueue

def after_submit(doc, method):
        try:
                doctype = doc.meta.get("name")
                if(doc.party_balance == doc.base_received_amount):
                        boski_manager(doc.party, "guest", allow_guest=True)
        except Exception as e:
                frappe.msgprint(e)

def send_payment_request(doc, method):
        try:
                doctype = doc.meta.get("name")
                if(doc.status == "Initiated"):
                        customer = frappe.get_doc("Customer", doc.party)
                        msg = """ <div>
                                Hi {name},
                                <br><br>
                                Your subscription is over. 
                                <br><br>
                                If you want to continue with GRYNN Service
                                <br><br>
                                click on the below link to confirm payment
                                <br><br>
                                {url}
                                <br><br>
                                Your subscription will be continued after verification
                                <br><br>
                                Thank you for choosing GRYNN.
                                <br><br>
                                Cheers,
                                <br><br>
                                GRYNN Team
                                </div>""".format(name=doc.party, url=doc.payment_url)

                        email_args = {
                                "recipients": [customer.email],
                                "subject": "Subscription Over",
                                "message": msg
                        }
                        enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
        except Exception as e:
                frappe.msgprint(e)
