"""
	Developer: Kartik Sharma
 	Email: kartik.sharma@grynn.in
"""

import frappe
from frappe import _
from frappe.utils import fmt_money, random_string, cint, nowdate
from frappe.geo.country_info import get_country_timezone_info
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request
from frappe.integrations.utils import get_payment_gateway_controller
from boski.utils.boski import check_site_name
import json

payment_gateway = {
    "INR" : "Razorpay",
    "USD" : "PayPal"
}
payment_gateway_account = {
    "INR" : "Razorpay - INR",
    "USD" : "PayPal - USD"
}

class ExpiredTokenException(Exception): pass

def get_context(context):
    
    context.no_cache = True

    context["countries"] = get_countries()
    context["industries"] = get_industries()
    context["timezones"] = get_timezones()
    context["currencies"] = get_currencies()
    context["languages"] = get_languages()
    context["plans"] = get_plans()
    print(context["plans"])
    return context

def get_industries():
    industries = frappe.db.sql('select name from tabDomain', as_list=True)
    industries = [industry[0] for industry in industries]
    return industries

def get_countries():
    countries = frappe.db.sql('select country_name from tabCountry order by name', as_list=True)
    countries = [country[0] for country in countries]
    return countries

def get_currencies():
    currency_codes = frappe.db.sql('select currency_name from tabCurrency', as_list=True)
    currency_codes = [code[0] for code in currency_codes]
    # print(currency_codes)
    return currency_codes

def get_languages():
    language_codes = frappe.db.sql('select language_code, language_name from tabLanguage order by name', as_dict=True)
    # print(language_codes)
    return language_codes    

def get_timezones():
    all_timezones = get_country_timezone_info()
    all_timezones = all_timezones["all_timezones"]
    return all_timezones

@frappe.whitelist(allow_guest=True)
def get_plans(currency=None):
    base_features = {
			'emails': '1000 emails / month',
			'space': '1 GB'
	}
    
    all_plans = frappe.db.sql('select item_name, item_code, name from tabItem where consulting_item=0 order by name desc', as_dict=True)

    base_plans = []
    # consulting_plans = []

    for plan in all_plans:    
        plan_price = get_plan_price(plan.item_code, currency or "USD")
        plan.update({
            "price": plan_price
        })
        # if not plan.consulting_item:
        base_plans.append(plan)
        # else:
            # consulting_plans.append(plan)
    print(base_plans)
    return {
        "base_plans": base_plans,
        # "consulting_plans": consulting_plans,
        "base_features": base_features
    }


def get_plan_price(item_code, currency):
    plan_price = frappe.db.sql('select price_list_rate from `tabItem Price` where item_code="{item_code}" and currency="{currency}" '.format(item_code=item_code, currency=currency), as_dict=True)
    print(plan_price)
    return fmt_money(plan_price[0].price_list_rate, currency=currency)


@frappe.whitelist(allow_guest=True)
def signup(cmd, email, first_name, last_name, subdomain):
    if check_site_name(subdomain):
        frappe.throw(_("Please choose another site name."))
    customer = frappe.new_doc("Customer")
    customer.customer_name = first_name + " "+ last_name
    customer.email = email
    customer.domain = subdomain
    customer.type = "Company"
    customer.customer_group = "All Customer Groups"
    customer.territory = "All Territories"

    customer.save(ignore_permissions=True)
    frappe.db.commit()

    reference = send_otp(customer)
    return {
        "email": customer.email,
        "location": "#verify",
        "reference" : reference 
    }
     

def send_otp(customer):
    code = random_string(6)
    recipients = customer.email
    subject = "Please confirm this email address for ERPNext"
    message = """<div> 	
                Hi <b>{name}</b>, 
                <br><br>
                You are one step away from accessing your grr.fyi account.
                <br>
                Below is the verification code to access your account.
                <br><br>
                Your Verification Code: <b>{code}</b>
                <br><br>
                Once you verify, we will finish setting up your account.
                <br>
                Thank you for choosing GRYNN.
                <br><br>
                Cheers,
                <br><br>
                GRYNN Team
                </div>
            """.format(name=customer.customer_name, code=code)
    frappe.sendmail(recipients=recipients, subject=subject, message=message,now=True )
    reference = frappe.generate_hash(length=8)
    expiry_time = 600
    frappe.cache().set(reference + '_token', code)
    frappe.cache().expire(reference + '_token', expiry_time)
    return reference


@frappe.whitelist(allow_guest=True)
def verify_otp(cmd, id, otp):
    cached_otp = frappe.cache().get(id + '_token')
    if not cached_otp:
        raise ExpiredTokenException(_('Token expired, click on Resend Code to get token again.'))
    print(otp, cached_otp)
    if not otp == cached_otp.decode("utf-8") :
        frappe.throw(_('OTP did not match. Try resending code again.'))
    else:
        return {
            "cmd": cmd,
            "id": id,
            "otp" : otp,
            "location" : "#other-details" 
        }

@frappe.whitelist(allow_guest=True)
def update_account(email, users=None, currency=None, billing=None):
    if not users and not currency and not billing:
        return
    try:
        customer = frappe.get_doc("Customer", {"email": email})
        customer.plan = billing
        # customer.consultingsupport = add_on
        customer.default_currency = currency
        customer.users = users 
        customer.save(ignore_permissions=True)
        frappe.db.commit()

    except frappe.DoesNotExistError:
        frappe.throw(_('Cannot update account for null.'))
    

@frappe.whitelist(allow_guest=True)
def get_total_cost(users, currency, billing_cycle, coupon=None):
    print(users, currency, billing_cycle, coupon) 

    billing_cycle_price = frappe.get_value("Item Price",{"item_code": billing_cycle, "currency":currency, "selling": 1},"price_list_rate")
    # add_on_price = 0 if add_ons == "0" else frappe.get_value("Item Price",{"item_code": add_ons, "currency":currency, "selling": 1},"price_list_rate")
    print(billing_cycle_price)

    total_cost = (billing_cycle_price * cint(users))
    discount = 0
    if coupon and frappe.db.exists("Coupon", coupon):
        total_cost, discount = apply_code(coupon, total_cost, currency)

    formatted_billing_price = (fmt_money((billing_cycle_price * cint(users)), currency=currency)).replace("'", ",")
    # formatted_add_on_price = (fmt_money(add_on_price, currency=currency)).replace("'",",")
    formatted_total_cost = (fmt_money(total_cost, currency=currency)).replace("'",",")
    formatted_discount = (fmt_money(discount, currency=currency)).replace("'",",")

    return {
        "billing_cost": formatted_billing_price,
        # "add_on" : formatted_add_on_price,
        "total_cost" : formatted_total_cost, 
        "discount": formatted_discount
    }


def apply_code(coupon, cost_without_coupon, currency):
    validity_date, discount_rate, max_discount, max_usage, times_used = frappe.get_value("Coupon", 
        {"name": coupon}, ["valid_till", "discount_percent", "maximum_discount_amount", "max_usage", "used"])

    if validity_date.strftime("%Y-%m-%d") < nowdate() or cint(times_used) >= max_usage:
        frappe.throw(_("Coupon has expired."))
    total_cost = 0
    discount_amount = (cost_without_coupon * discount_rate) / 100

    #convert max_discount from company currency to customer currency
    max_discount = max_discount * 1.01 if currency == "USD" else max_discount * 71    ##  1 CHF = 1.01 USD,  1 CHF = 71 INR

    
    if discount_amount >= max_discount:
        total_cost = cost_without_coupon - max_discount
        return [total_cost, max_discount]
    else:
        total_cost = cost_without_coupon - discount_amount
        return [total_cost, discount_amount]
    
@frappe.whitelist(allow_guest=True)
def register(args):
    try:
        args = json.loads(args)
        users, currency, billing_cycle, coupon, email = args['users'], args['currency'], args['billing_cycle'],args['coupon'],args['email']
        price_list = frappe.get_value("Price List", {"currency": currency, "selling": 1, "enabled": 1})

        billing_cycle_price = frappe.get_value("Item Price",{"item_code": billing_cycle, "currency":currency, "selling": 1},"price_list_rate")
        # add_on_price = 0 if add_ons == "0" else frappe.get_value("Item Price",{"item_code": add_ons, "currency":currency, "selling": 1},"price_list_rate")

        total_cost = (billing_cycle_price * cint(users))
        discount = 0

        if coupon:
            total_cost, discount = apply_code(coupon, total_cost, currency) 

        customer, customer_email = frappe.get_value("Customer", {"email": email }, ["name", "email"])
        frappe.db.set_value("Customer", customer, "users", users)
        frappe.db.commit()
        
        sales_order = make_sales_order(customer,currency, price_list, discount, users, billing_cycle, coupon)
        
        si = make_sales_invoice(sales_order.name,ignore_permissions=True)
        si.insert(ignore_permissions=True)
        si.submit()
        
        update_coupon_usage(coupon)

        payment_request = make_payment_request(dt="Sales Invoice", dn=si.name, submit_doc=True, mute_email=True, payment_gateway= payment_gateway_account[currency])
        
        payment_details = get_payment_details(payment_request ,si, customer,customer_email, currency)

        controller = get_payment_gateway_controller(payment_gateway[currency])
        url = controller.get_payment_url(**payment_details)
        print(controller, url)
        return url
    except Exception as e:
        print(e)
        print(frappe.get_traceback())

def get_payment_details(payment_request ,si, customer,customer_email, currency):
    return {
		"amount": si.grand_total,
		"title": payment_request.reference_name,
		"description": payment_request.subject,
		"reference_doctype":payment_request.doctype,
		"reference_docname": payment_request.name,
		"payer_email": customer_email,
		"payer_name": customer,
		"order_id": payment_request.reference_name,
		"currency": payment_request.currency,
		"payment_gateway": payment_gateway[currency],
		# "subscription_details": {
		# 	"plan_id": "plan_12313", # if Required
		# 	"start_date": "2018-08-30",
		# 	"billing_period": "Month" #(Day, Week, SemiMonth, Month, Year),
		# 	"billing_frequency": 1,
		# 	"customer_notify": 1,
		# 	"upfront_amount": 1000
		# }
	}

def update_coupon_usage(coupon):
    times_used = frappe.get_value("Coupon", coupon, "used")
    coupon_usage = cint(times_used) + 1
    frappe.db.set_value("Coupon", coupon,"used", coupon_usage)
    frappe.db.commit()
        
def make_sales_order(customer,currency, price_list, discount, users, billing_cycle=None, coupon=None):
    try:
        sales_order = frappe.new_doc("Sales Order")
        sales_order.customer = customer
        sales_order.currency = currency
        sales_order.coupon = coupon
        sales_order.delivery_date = nowdate()
        sales_order.selling_price_list = price_list
        sales_order.discount_amount = discount
    
        if billing_cycle:
            sales_order.append("items",{
                "item_code": billing_cycle,
			    "item_name": billing_cycle,
                "qty": cint(users),
                "delivery_date": nowdate()
            })

        # if add_ons and add_ons != "0":
        #     sales_order.append("items",{
        #         "item_code": add_ons,
		#     	"item_name": add_ons,
        #         "qty": 1,
        #         "delivery_date": nowdate()    
        #     })
        sales_order.insert(ignore_permissions=True)
        sales_order.submit()

        return sales_order
    except Exception as e:
        print(frappe.get_traceback())
