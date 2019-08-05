"""
    Dveloper Sahil Saini
    Email sahil.saini@grynn.in

"""

import frappe
from frappe.utils.__init__ import get_sites
from subprocess import check_output, Popen, PIPE
import os, re, json, time, pymysql, shlex
from frappe import _, throw, msgprint
from pathlib import Path

@frappe.whitelist()
def boski_manager(site_name):
        commands = []
        if(site_name):
                installable_apps = get_installable_apps()
                admin_password = frappe.generate_hash()
                mysql_root_password = get_verify_password()
                commands = ["bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} {site_name}".format(site_name=site_name, 
                            admin_password=admin_password, mysql_password=mysql_root_password)]

                if('erpnext' not in installable_apps):
                        commands.append("bench get-app erpnext")
                commands.append("bench --site {site_name} install-app erpnext".format(site_name=site_name))
                print(commands)
                frappe.enqueue('boski.utils.boski.boski_command_manage', commands=commands)
        else:
                frappe.throw(_("Kindly Provide Domain Name."))

def get_installable_apps():
        app_list_file = 'apps.txt'
        with open(app_list_file, "r") as f:
                apps = f.read().split('\n')

        apps_not_required = ['frappe', 'boski']
        installable_apps = set(apps) - set(apps_not_required)
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


def boski_command_manage(commands):
        print(commands)
        log_commands = " && ".join(commands)
        print(log_commands)


def string_decode(string, encoding = 'utf-8'):
        try:
                string = string.decode(encoding)
        except Exception as e:
                pass
                return string
        
