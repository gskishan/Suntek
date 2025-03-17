import frappe


def toggle_solar_ambassador_integration(enable: bool = True):
    try:
        status = "Enabled" if enable else "Disabled"

        suntek_settings = frappe.get_doc(
            "Suntek Settings", "Suntek Settings", for_update=True
        )

        if suntek_settings.solar_ambassador_integration_status != status:
            suntek_settings.solar_ambassador_integration_status = status
            suntek_settings.save(ignore_permissions=True)
            frappe.db.commit()

            print(f"Solar Ambassador Integration set to {status}")
        else:
            print(f"Solar Ambassador Integration was already {status}")

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Failed to toggle Solar Ambassador Integration: {str(e)}")
        print(f"Error toggling Solar Ambassador Integration: {str(e)}")
