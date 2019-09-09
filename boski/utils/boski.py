"""
    Dveloper Sahil Saini
    Email sahil.saini@grynn.in

"""

import frappe
from frappe.utils.__init__ import get_sites
import subprocess
from subprocess import check_output, Popen, PIPE
import os, re, json, time, pymysql, shlex
from frappe import _, throw, msgprint
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
import re, shlex
import time
from frappe.utils.background_jobs import enqueue
from frappe.utils import fmt_money, random_string, cint, nowdate

@frappe.whitelist()
def boski_manager(name, key, allow_guest=True):
        commands = []
        doc = frappe.get_doc("Customer", {"name": name})
        site_in = check_site_name(str(doc.domain))
        if(not site_in):
                domain = (str(doc.domain)+".grr.fyi")
                installable_apps = get_installable_apps()
                admin_password = random_string(6)
                mysql_root_password = get_verify_password()
                commands = ["bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} {site_name}".format(site_name=domain, admin_password=admin_password, mysql_password=mysql_root_password)]
                
                if('erpnext' not in installable_apps):
                        commands.append("bench get-app erpnext")
                commands.append("bench --site {site_name} install-app erpnext".format(site_name=domain))
                commands.append("bench setup add-domain --site {site_name} {site_name}".format(site_name=domain))
                commands.append("bench --site {site_name} enable-scheduler".format(site_name=domain))
                commands.append("bench --site {site_name} set-limits --limit users {user} --limit emails 1000".format(site_name=domain, user=int(doc.users)))
                frappe.enqueue('boski.utils.boski.boski_command_manager', key=key, commands=commands, site_name=domain, password=admin_password, email=doc.email)
        else:
                frappe.throw(_("Thanks for choosing GRYNN...!!!"))

def get_installable_apps():
        app_list_file = 'apps.txt'
        with open(app_list_file, "r") as f:
                apps = f.read().split('\n')

        apps_not_required = ['frappe', 'boski']
        installable_apps = set(apps) - set(apps_not_required)
        print(installable_apps)
        return [x for x in installable_apps]

def get_verify_password():
        try:
                file_path = str(Path.home())+'/passwords.txt'
                with open(file_path, 'r') as f:
                        file_data = json.loads(f.read())
                    
                mysql_root_password = file_data['mysql_root_password']
                try:
                        db = pymysql.connect(host=frappe.conf.db_host or 'localhost', user='root' ,passwd=mysql_root_password)
                        db.close()
                        return mysql_root_password
                except Exception as e:
                        frappe.throw(_("MySQL password is incorrect"))
        except Exception as e:
                frappe.throw(_("Password file not found."))


def boski_command_manager(key, commands, site_name, password, email):
        log_commands = " && ".join(commands)
        frappe.publish_realtime(key, "Sit Tight With US and Feel the GRYNN Magic...!!!\n\n\n", user=frappe.session.user)
        frappe.publish_realtime(key, "Getting Ready:\n\n", user=frappe.session.user)
        try:
                for command in commands:
                        terminal = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd="..")
                        for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
                                print(c)
                                frappe.publish_realtime(key, c, user=frappe.session.user)

                if terminal.wait():
                        frappe.msgprint(_("Process Failed."))
                else:
                        frappe.msgprint(_("Process Successful."))
                        frappe.publish_realtime(key, "\n\nYour Site is Ready. Thanks For Choosing GRYNN...!!!", user=frappe.session.user)
                        try:
                                msg = """<div>
                                        Hey,
                                        <br><br>
                                        Thanks for choosing GRYNN. 
                                        <br><br>
                                        {site_name} is now ready. 
                                        <br><br>
                                        Login id: Administrator.
                                        <br><br>
                                        Password: {password} .
                                        <br><br>
                                        Cheers,
                                        <br><br>
                                        GRYNN Team
                                        </div>
                                        """.format(site_name=site_name, password=password)
                                
                                email_args = {
                                            "recipients": [email],
                                            "subject": "Your Domain is Ready",
                                            "message": msg
                                }
                                enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
                        except Exception as e:
                                frappe.throw(_("{0}").format(e))
        except Exception as e:
                frappe.throw(_("Kindly contact to admin with the error screen shot. {0}").format(e))


@frappe.whitelist(allow_guest=True)
def check_site_name(site):
    site = site + ".grr.fyi"
    print(site)
    return bytes(site, 'utf-8') in check_output("ls")


def safe_decode(string, encoding = 'utf-8'):
        try:
                string = string.decode(encoding)
        except Exception:
                pass
        return string
