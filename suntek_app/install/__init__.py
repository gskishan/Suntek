import frappe

from suntek_app.channel_partner import setup_channel_partner


def before_install():
    if not frappe.db.exists("Role", "Channel Partner"):
        setup_channel_partner()
