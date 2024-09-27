from frappe import _

def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_custom_enquiry_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "enquiry_owner",
            "label": _("Enquiry Owner"),
            "fieldtype": "Link",
            "options": "User",
            "width": "130",
        },
        {"fieldname": "total_enquiry", "label": _("Total Enquiry's"), "fieldtype": "Int", "width": "130"},
        {"fieldname": "interested", "label": _("Interested"), "fieldtype": "Int", "width": "100"},
        {"fieldname": "opportunity", "label": _("Opportunity"), "fieldtype": "Int", "width": "100"},
        {"fieldname": "open", "label": _("Open"), "fieldtype": "Int", "width": "100"},
        {"fieldname": "quotation", "label": _("Quotation"), "fieldtype": "Int", "width": "100"},
        {"fieldname": "converted", "label": _("Converted"), "fieldtype": "Int", "width": "100"},
        {"fieldname": "do_not_contact", "label": _("Do Not Contact"), "fieldtype": "Int", "width": "120"},
        {"fieldname": "lost", "label": _("Lost"), "fieldtype": "Int", "width": "80"},
    ]

def get_custom_enquiry_data(filters):
    # SQL query to get the enquiry data based on the 'status' field options
    query = """
    SELECT 
        custom_enquiry_owner_name AS enquiry_owner,
        COUNT(*) AS total_enquiry,
        COUNT(CASE WHEN status = 'Interested' THEN 1 END) AS interested,
        COUNT(CASE WHEN status = 'Opportunity' THEN 1 END) AS opportunity,
        COUNT(CASE WHEN status = 'Open' THEN 1 END) AS open,
        COUNT(CASE WHEN status = 'Quotation' THEN 1 END) AS quotation,
        COUNT(CASE WHEN status = 'Converted' THEN 1 END) AS converted,
        COUNT(CASE WHEN status = 'Do Not Contact' THEN 1 END) AS do_not_contact,
        COUNT(CASE WHEN status = 'Lost' THEN 1 END) AS lost
    FROM 
        tabLead
    GROUP BY 
        custom_enquiry_owner_name
    """
    
    # Execute the query and fetch the data
    data = frappe.db.sql(query, as_dict=True)
    
    return data
