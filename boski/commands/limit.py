from __future__ import unicode_literals, absolute_import, print_function
import click
import hashlib, os, sys, compileall, re
import frappe
from frappe import _
from frappe.commands import pass_context, get_site
from frappe.commands.scheduler import _is_scheduler_enabled
from boski.limits import update_limits, get_limits
from frappe.installer import update_site_config
from frappe.utils import touch_file, get_site_path
from six import text_type

# imports - third-party imports
from pymysql.constants import ER

@click.command('set-limit')
@click.option('--site', help='site name')
@click.argument('limit')
@click.argument('value')
@pass_context
def set_limit(context, site, limit, value):
        """Sets user / space / email limit for a site"""
        _set_limits(context, site, ((limit, value),))


@click.command('set-limits')
@click.option('--site', help='site name')
@click.option('--limit', 'limits', type=(text_type, text_type), multiple=True)
@pass_context
def set_limits(context, site, limits):
        _set_limits(context, site, limits)

def _set_limits(context, site, limits):
        import datetime
        
        if not limits:
                return

        if not site:
                site = get_site(context)
        
        with frappe.init_site(site):
                frappe.connect()
                new_limits = {}
                for limit, value in limits:
                        if limit not in ('daily_emails', 'emails', 'space', 'users', 'email_group', 'currency',
                                    'expiry', 'support_email', 'support_chat', 'upgrade_url', 'subscription_id',
                                    'subscription_type', 'current_plan', 'subscription_base_price', 'upgrade_plan',
                                    'upgrade_base_price', 'cancellation_url'):
                                    frappe.throw(_('Invalid limit {0}').format(limit))
                        if limit=='expiry' and value:
                                try:
                                        datetime.datetime.strptime(value, '%Y-%m-%d')
                                except ValueError:
                                        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

                        elif limit in ('space', 'subscription_base_price', 'upgrade_base_price'):
                                value = float(value)

                        elif limit in ('users', 'emails', 'email_group', 'daily_emails'):
                                value = int(value)

                        new_limits[limit] = value

                update_limits(new_limits)
