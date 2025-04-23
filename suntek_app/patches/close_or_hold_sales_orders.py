import json
import os

import frappe


def execute():
    """
    Updates sales order statuses based on the data in so_by_status.json file.
    Sets orders to "On Hold" or "Closed" depending on which array they fall in.
    """
    # Get file path
    file_path = frappe.get_app_path("suntek_app", "patches", "so_by_status.json")

    # Load the JSON data
    with open(file_path, "r") as f:
        data = json.load(f)

    # Process orders to be put on hold
    hold_orders = data.get("hold", [])
    successful_hold = 0
    for sales_order in hold_orders:
        try:
            if not frappe.db.exists("Sales Order", sales_order):
                print(f"Sales Order {sales_order} not found")
                continue

            doc = frappe.get_doc("Sales Order", sales_order)
            if doc.docstatus == 1 and doc.status != "On Hold":
                # Update the status to "On Hold"
                doc.update_status("On Hold")
                doc.flags.ignore_permissions = True
                doc.save()
                frappe.db.commit()
                successful_hold += 1
                print(f"Updated {sales_order} to 'On Hold'")
        except Exception as e:
            frappe.db.rollback()
            print(f"Error updating {sales_order} to 'On Hold': {e}")

    # Process orders to be closed
    close_orders = data.get("close", [])
    successful_close = 0
    for sales_order in close_orders:
        try:
            if not frappe.db.exists("Sales Order", sales_order):
                print(f"Sales Order {sales_order} not found")
                continue

            doc = frappe.get_doc("Sales Order", sales_order)
            if doc.docstatus == 1 and doc.status != "Closed":
                # Update the status to "Closed"
                doc.update_status("Closed")
                doc.flags.ignore_permissions = True
                doc.save()
                frappe.db.commit()
                successful_close += 1
                print(f"Updated {sales_order} to 'Closed'")
        except Exception as e:
            frappe.db.rollback()
            print(f"Error updating {sales_order} to 'Closed': {e}")

    print(f"Successfully updated: {successful_hold} hold orders and {successful_close} close orders")
    print(f"Total processed: {len(hold_orders)} hold orders and {len(close_orders)} close orders")


def update_sales_order(sales_order, status):
    """
    Updates the status of a Sales Order

    Args:
        sales_order (str): The name of the Sales Order
        status (str): The new status ("On Hold" or "Closed")
    """
    # Check if the order exists
    if not frappe.db.exists("Sales Order", sales_order):
        print(f"Sales Order {sales_order} not found")
        return

    # Get the doc
    doc = frappe.get_doc("Sales Order", sales_order)

    # Update status
    if doc.status != status:
        doc.status = status
        doc.flags.ignore_permissions = True
        doc.save()
