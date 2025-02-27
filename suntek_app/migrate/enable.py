import frappe


def solar_ambassador_integration():
    suntek_settings = frappe.get_doc("Suntek Settings")

    suntek_settings.solar_ambassador_integration_status = "Enabled"
    suntek_settings.save()
    frappe.db.commit()
    print(
        f"Solar Ambassador Integration set to {suntek_settings.solar_ambassador_integration_status}"
    )
