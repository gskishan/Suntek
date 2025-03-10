import frappe

from suntek_app.suntek.utils.api_handler import (
    create_api_response,
    parse_request_data,
    validate_auth_token,
)


@frappe.whitelist(allow_guest=True)
def create_solar_ambassador():
    """
    Request Body:
    {
        "name": "Ambassador Name",
        "mobile_number": "1234567890",
        "email_id": "email@example.com",
        "state": "State Name",
        "city": "City Name",
        "district": "District Name",
        "bank_name": "Bank Name",
        "bank_account_number": "Account Number",
        "ifsc_code": "IFSC Code",
        "aadhar_number": "123456789012",
        "aadhar_front": "base64_or_url",
        "aadhar_back": "base64_or_url",
        "pan_number": "ABCDE1234F",
        "pan_card": "base64_or_url",
    }
    """
    if frappe.request.headers.get(
        "X-Django-Server-Authorization"
    ) and validate_auth_token(
        frappe.request.headers.get("X-Django-Server-Authorization")
    ):
        if not frappe.request.method == "POST":
            return create_api_response(405, "method not allowed", "Method Not Allowed")

        frappe.set_user("developer@suntek.co.in")
        data = parse_request_data(frappe.request.data)

        ambassador_name = data.get("name")
        mobile_no = data.get("mobile_number")

        if not ambassador_name or not mobile_no:
            return create_api_response(
                400, "bad request", "Missing Name or Mobile Number"
            )

        existing = frappe.db.exists(
            "Ambassador", {"ambassador_mobile_number": mobile_no}
        )
        if existing:
            return create_api_response(
                409, "conflict", "Ambassador with this mobile number already exists"
            )

        try:
            ambassador = frappe.new_doc("Ambassador")
            ambassador.update(
                {
                    "ambassador_name": ambassador_name,
                    "ambassador_mobile_number": mobile_no,
                    "email_id": data.get("email_id"),
                    "state": data.get("state"),
                    "city": data.get("city"),
                    "district": data.get("district"),
                    "type_of_account": data.get("type_of_account"),
                    "bank_name": data.get("bank_name"),
                    "bank_account_number": data.get("bank_account_number"),
                    "ifsc_code": data.get("ifsc_code"),
                    "aadhar_number": data.get("aadhar_number"),
                    "aadhar_front": data.get("aadhar_front"),
                    "aadhar_back": data.get("aadhar_back"),
                    "pan_number": data.get("pan_number"),
                    "pan_card": data.get("pan_card"),
                }
            )

            ambassador.save()
            frappe.db.commit()

            response_data = dict(data)
            response_data["ambassador_id"] = ambassador.name

            return create_api_response(
                201, "created", "Ambassador created successfully", data=response_data
            )
        except Exception as e:
            return create_api_response(400, "bad_request", str(e))

    return create_api_response(401, "unauthorized", "Missing or Invalid auth")


@frappe.whitelist(allow_guest=True)
def update_solar_ambassador():
    """
    Request Body:
    {
        "mobile_number": "1234567890",

        "name": "Updated Name",
        "email_id": "updated@example.com",
        "state": "Updated State",
        "city": "Updated City",
        "district": "Updated District",
        "bank_name": "Updated Bank",
        "bank_account_number": "Updated Account",
        "ifsc_code": "Updated IFSC",
        "aadhar_number": "123456789012",
        "aadhar_front": "base64_or_url",
        "aadhar_back": "base64_or_url",
        "pan_number": "ABCDE1234F",
        "pan_card": "base64_or_url",
    }
    """
    if frappe.request.headers.get(
        "X-Django-Server-Authorization"
    ) and validate_auth_token(
        frappe.request.headers.get("X-Django-Server-Authorization")
    ):
        if not frappe.request.method == "PUT":
            return create_api_response(405, "method not allowed", "Method Not Allowed")

        frappe.set_user("developer@suntek.co.in")
        data = parse_request_data(frappe.request.data)

        mobile_no = data.get("mobile_number")
        if not mobile_no:
            return create_api_response(400, "bad request", "Missing Mobile Number")

        ambassador_name = frappe.db.get_value(
            "Ambassador", {"ambassador_mobile_number": mobile_no}, "name"
        )

        if not ambassador_name:
            return create_api_response(
                404, "not found", "Ambassador not found with the provided mobile number"
            )

        try:
            ambassador = frappe.get_doc("Ambassador", ambassador_name)

            field_mapping = {
                "name": "ambassador_name",
                "email_id": "email_id",
                "state": "state",
                "city": "city",
                "district": "district",
                "type_of_account": "type_of_account",
                "bank_name": "bank_name",
                "bank_account_number": "bank_account_number",
                "ifsc_code": "ifsc_code",
                "aadhar_number": "aadhar_number",
                "aadhar_front": "aadhar_front",
                "aadhar_back": "aadhar_back",
                "pan_number": "pan_number",
                "pan_card": "pan_card",
            }

            updated_fields = {}

            for payload_field, doc_field in field_mapping.items():
                if payload_field in data:
                    ambassador.set(doc_field, data[payload_field])
                    updated_fields[doc_field] = data[payload_field]

            if not updated_fields:
                return create_api_response(
                    400, "bad_request", "No fields provided for update"
                )

            ambassador.save()
            frappe.db.commit()

            response_data = {
                "ambassador_id": ambassador.name,
                "mobile_number": mobile_no,
                "updated_fields": updated_fields,
            }

            return create_api_response(
                200, "success", "Ambassador updated successfully", data=response_data
            )
        except Exception as e:
            return create_api_response(400, "bad_request", str(e))

    return create_api_response(401, "unauthorized", "Missing or Invalid auth")
