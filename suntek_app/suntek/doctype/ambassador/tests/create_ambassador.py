import frappe


def create_valid_ambassador():
    """Create a valid ambassador for testing."""
    try:
        new_frappe_ambassador = frappe.get_doc(
            {
                "doctype": "Ambassador",
                "ambassador_name": "Test Ambassador",
                "ambassador_mobile_number": "9595959595",
                "email_id": "test@test.com",
                "pan_number": "HHHHH4444Q",
                "aadhar_number": "123456789012",
            }
        )
        new_frappe_ambassador.insert()
        frappe.db.commit()  # Ensure the record is committed to the database
        return new_frappe_ambassador
    except Exception:
        frappe.db.rollback()
        raise


def create_ambassador_with_invalid_pan():
    """Create an ambassador with an invalid PAN number for testing validation."""
    try:
        new_frappe_ambassador = frappe.get_doc(
            {
                "doctype": "Ambassador",
                "ambassador_name": "Test Ambassador",
                "ambassador_mobile_number": "9595959595",
                "email_id": "test@test.com",
                "pan_number": "ahsodhasoidhaoi",  # Invalid PAN format
                "aadhar_number": "123456789012",
            }
        )
        new_frappe_ambassador.insert()
        frappe.db.commit()  # Ensure the record is committed to the database
        return new_frappe_ambassador
    except Exception:
        frappe.db.rollback()
        raise


def create_ambassador_with_invalid_aadhar():
    """Create an ambassador with an invalid Aadhar number for testing validation."""
    try:
        new_frappe_ambassador = frappe.get_doc(
            {
                "doctype": "Ambassador",
                "ambassador_name": "Test Ambassador",
                "ambassador_mobile_number": "9595959595",
                "email_id": "test@test.com",
                "pan_number": "HHHHH4444Q",
                "aadhar_number": "12345",  # Invalid Aadhar format (should be 12 digits)
            }
        )
        new_frappe_ambassador.insert()
        frappe.db.commit()  # Ensure the record is committed to the database
        return new_frappe_ambassador
    except Exception:
        frappe.db.rollback()
        raise
