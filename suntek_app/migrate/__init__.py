import frappe

from suntek_app.migrate.setup_project_boilerplate import setup_boilerplate
from suntek_app.migrate.toggle_solar_ambassador_integration_status import (
    toggle_solar_ambassador_integration,
)
from suntek_app.utils.permissions import remove_duplicate_permissions


def before_migrate():
    toggle_solar_ambassador_integration(enable=False)

    if not frappe.db.exists("Role", "Sales Master Manager"):
        sales_master_manager_role = frappe.new_doc("Role")
        sales_master_manager_role.update({"role_name": "Sales Master Manager", "desk_access": 1})
        sales_master_manager_role.insert()
        print("Created Sales Master Manager role")

    if not frappe.db.exists("Role", "Lead Master Manager"):
        lead_master_manager = frappe.new_doc("Role")
        lead_master_manager.update({"role_name": "Lead Master Manager", "desk_access": 1})
        lead_master_manager.insert()
        print("Created Lead Master Manager role")


def after_migrate():
    remove_duplicate_permissions()
    toggle_solar_ambassador_integration()

    # Create Boilerplate Project Data
    setup_boilerplate()
