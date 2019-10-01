import frappe
from frappe.integrations.utils import get_payment_gateway_controller


@frappe.whitelist()
def paypal():
	try:
		controller = get_payment_gateway_controller("PayPal")
		controller().validate_transaction_currency("USD")

		payment_details = {
			"amount": 600,
			"title": "Payment for bill : 111",
			"description": "payment via cart",
			"reference_doctype": "Payment Request",
			"reference_docname": "PR0001",
			"payer_email": "NuranVerkleij@example.com",
			"payer_name": "Nuran Verkleij",
			"order_id": "111",
			"currency": "USD",
			"payment_gateway": "Paypal",
			"subscription_details": {
				"plan_id": "plan_12313",  # if Required
				"start_date": "2018-08-30",
				"billing_period": "Month",  # (Day, Week, SemiMonth, Month, Year),
				"billing_frequency": 1,
				"customer_notify": 1,
				"upfront_amount": 1000
			}
		}

		url = controller().get_payment_url(**payment_details)

		print(url)	
	except Exception as e:
		print(frappe.get_traceback())
