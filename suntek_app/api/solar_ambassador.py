import frappe

from suntek_app.suntek.utils.api_handler import (
    create_api_response,
    parse_request_data,
    validate_auth_token,
)


@frappe.whitelist(allow_guest=True)
def create_solar_ambassador():
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

        # Check if ambassador with the same mobile already exists
        existing = frappe.db.exists(
            "Ambassador", {"ambassador_mobile_number": mobile_no}
        )
        if existing:
            return create_api_response(
                409, "conflict", "Ambassador with this mobile number already exists"
            )

        email_id = data.get("email_id")
        gender = data.get("gender")
        state = data.get("state")
        district = data.get("district")
        bank_name = data.get("bank_name")
        bank_account_number = data.get("bank_account_number")
        ifsc_code = data.get("ifsc_code")
        aadhar_card_url = data.get("aadhar_card_url")
        pan_card_url = data.get("pan_card_url")

        try:
            ambassador = frappe.new_doc("Ambassador")

            ambassador.update(
                {
                    "ambassador_name": ambassador_name,
                    "ambassador_mobile_number": mobile_no,
                    "email_id": email_id,
                    "gender": gender,
                    "state": state,
                    "district": district,
                    "bank_name": bank_name,
                    "bank_account_number": bank_account_number,
                    "ifsc_code": ifsc_code,
                    "aadhar_card_url": aadhar_card_url,
                    "pan_card_url": pan_card_url,
                }
            )

            ambassador.save()
            frappe.db.commit()

            response_data = dict(data)
            response_data["ambassador_id"] = (
                ambassador.name
            )  # Include ERP ID in response

            return create_api_response(
                201, "created", "Ambassador created successfully", data=response_data
            )
        except Exception as e:
            return create_api_response(400, "bad_request", str(e))

    return create_api_response(401, "unauthorized", "Missing or Invalid auth")


@frappe.whitelist(allow_guest=True)
def update_solar_ambassador():
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

        # Find ambassador by mobile number
        ambassador_name = frappe.db.get_value(
            "Ambassador", {"ambassador_mobile_number": mobile_no}, "name"
        )

        if not ambassador_name:
            return create_api_response(
                404, "not found", "Ambassador not found with the provided mobile number"
            )

        try:
            ambassador = frappe.get_doc("Ambassador", ambassador_name)

            # Update fields if provided
            if data.get("name"):
                ambassador.ambassador_name = data.get("name")

            if data.get("email_id"):
                ambassador.email_id = data.get("email_id")

            if data.get("gender"):
                ambassador.gender = data.get("gender")

            if data.get("state"):
                ambassador.state = data.get("state")

            if data.get("district"):
                ambassador.district = data.get("district")

            if data.get("bank_name"):
                ambassador.bank_name = data.get("bank_name")

            if data.get("bank_account_number"):
                ambassador.bank_account_number = data.get("bank_account_number")

            if data.get("ifsc_code"):
                ambassador.ifsc_code = data.get("ifsc_code")

            if data.get("aadhar_card_url"):
                ambassador.aadhar_card_url = data.get("aadhar_card_url")

            if data.get("pan_card_url"):
                ambassador.pan_card_url = data.get("pan_card_url")

            ambassador.save()
            frappe.db.commit()

            response_data = dict(data)
            response_data["ambassador_id"] = (
                ambassador.name
            )  # Include ERP ID in response

            return create_api_response(
                200, "success", "Ambassador updated successfully", data=response_data
            )
        except Exception as e:
            return create_api_response(400, "bad_request", str(e))

    return create_api_response(401, "unauthorized", "Missing or Invalid auth")
