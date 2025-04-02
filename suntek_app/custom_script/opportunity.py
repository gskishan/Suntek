import frappe


@frappe.whitelist()
def get_emp(user):
    sql = f"""
        SELECT 
            e.cell_number,
            s.name 
        FROM `tabEmployee` e 
        INNER JOIN `tabSales Person` s 
            ON e.name = s.employee 
        WHERE user_id = "{user}"
    """
    data = frappe.db.sql(sql, as_dict=True)
    if data:
        return data


def get_salesman_user(self):
    sql = f"""
        SELECT 
            e.name,
            user_id 
        FROM `tabSales Person` s 
        INNER JOIN `tabEmployee` e 
            ON s.employee = e.name 
        WHERE s.employee IS NOT NULL 
            AND s.name = "{self.custom_sales_excecutive}" 
            AND e.user_id IS NOT NULL
    """
    return frappe.db.sql(sql, as_dict=True)
