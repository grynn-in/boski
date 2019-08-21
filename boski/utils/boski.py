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

@frappe.whitelist()
def boski_manager(email):
        commands = []
        doc = frappe.get_doc("Customer", {"email": email})
        if(doc.domain):
                domain = (str(doc.domain)+".grr.fyi")
                installable_apps = get_installable_apps()
                admin_password = doc.password
                mysql_root_password = "grynn@999"
                commands = ["bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} {site_name}".format(site_name=domain, admin_password=admin_password, mysql_password=mysql_root_password)]
                
                if('erpnext' not in installable_apps):
                        commands.append("bench get-app erpnext")
                commands.append("bench --site {site_name} install-app erpnext".format(site_name=domain))
                commands.append("bench setup add-domain --site {site_name} {site_name}".format(site_name=domain))
                boski_command_manage(commands, domain)
        else:
                frappe.throw(_("Kindly Provide Domain Name."))

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


def boski_command_manage(commands, site_name):
        log_commands = " && ".join(commands)
        key = "installing"
        try:
                for command in commands:
                        terminal = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd="..")
                        for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
                                frappe.publish_realtime(key, c, user=frappe.session.user)

                if terminal.wait():
                        frappe.msgprint(_("Process Failed."))
                else:
                        frappe.msgprint(_("Process Successful."))
        except Exception as e:
                frappe.throw(_("Kindly contact to admin with the error screen shot. {0}").fprmat(e))


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
