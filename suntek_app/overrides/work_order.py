from datetime import datetime

import frappe
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder as ERPNextWorkOrder
from frappe.model.naming import make_autoname


class CustomWorkOrder(ERPNextWorkOrder):
    def autoname(self):
        if self.naming_series == "SESPL-WO-FY-":
            fy = frappe.defaults.get_global_default("fiscal_year") or ""

            if not fy:
                fiscal_years = frappe.get_all(
                    "Fiscal Year", filters={"disabled": 0}, order_by="year_start_date desc", limit=1
                )
                if fiscal_years:
                    fy = frappe.get_doc("Fiscal Year", fiscal_years[0].name).name

            if fy and "-" in fy:
                start, end = fy.split("-")
                fy_short = f"{start[-2:]}-{end[-2:]}"
            else:
                year = datetime.today().year
                fy_short = f"{str(year)[-2:]}-{str(year + 1)[-2:]}"

            self.name = make_autoname(f"SESPL-WO-{fy_short}-.#####")
        else:
            self.name = make_autoname(self.naming_series)

