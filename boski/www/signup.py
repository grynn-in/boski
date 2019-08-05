"""
	Developer: Kartik Sharma
 	Email: kartik.sharma@grynn.in
"""

import frappe
from frappe.geo.country_info import get_country_timezone_info

def get_context(context):
    context["countries"] = get_countries()
    context["industries"] = get_industries()
    context["timezones"] = get_timezones()
    context["currencies"] = get_currencies()
    context["languages"] = get_languages()
    #print(context)
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
    print(currency_codes)
    return currency_codes

def get_languages():
    language_codes = frappe.db.sql('select language_code, language_name from tabLanguage order by name', as_dict=True)
    # print(language_codes)
    return language_codes    

def get_timezones():
    all_timezones = get_country_timezone_info()
    all_timezones = all_timezones["all_timezones"]
    return all_timezones
