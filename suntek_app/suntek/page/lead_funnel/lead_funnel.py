
import frappe
from frappe import _


LEAD_STATUSES = {
    "Total Leads": "#2E86C1",
    "Connected": "#F1C40F",
    "Interested": "#E67E22",
    "Quotation": "#D35400",
    "Converted": "#27AE60",
}


class LeadFunnel:
    def __init__(self):
        self.filters = {}

    def get_lead_data(
        self,
        from_date: str,
        to_date: str,
        company: str,
        lead_owner: str | None = None,
        source: str | None = None,
        department: str | None = None,
    ) -> list[dict]:
        """
        Get lead funnel data with owner details for tooltip
        """
        base_filters = self._get_base_filters(from_date, to_date, company)
        additional_conditions, additional_values = self._get_additional_filters(
            lead_owner, source, department
        )
        status_counts, others_count, owner_details = self._get_lead_counts(
            base_filters, additional_conditions, additional_values
        )

        return self._prepare_funnel_data(status_counts, others_count, owner_details)

    def _get_base_filters(self, from_date: str, to_date: str, company: str) -> tuple:
        """
        Prepare base filters for lead query
        """
        return (from_date, to_date, company)

    def _get_additional_filters(
        self,
        lead_owner: str | None,
        source: str | None,
        department: str | None,
    ) -> tuple[str, list]:
        """
        Prepare additional filters based on lead owner and source
        """
        conditions = []
        values = []

        if lead_owner:
            conditions.append("lead_owner = %s")
            values.append(lead_owner)
        if source:
            conditions.append("source = %s")
            values.append(source)
        if department:
            conditions.append("custom_department = %s")
            values.append(department)

        additional_conditions = f"AND {' AND '.join(conditions)}" if conditions else ""

        return additional_conditions, values

    def _get_lead_counts(
        self,
        base_filters: tuple,
        additional_conditions: str,
        additional_values: list,
    ) -> tuple[dict, int, dict]:
        """
        Get lead counts and owner details for each stage
        """

        total_leads_query = f"""
            SELECT 
                COUNT(*) as count,
                lead_owner,
                COUNT(lead_owner) as owner_count
            FROM `tabLead`
            WHERE date(`creation`) between %s and %s
            AND company = %s
            {additional_conditions}
            GROUP BY lead_owner-4
            ORDER BY owner_count DESC
        """

        status_query = f"""
            SELECT 
                status,
                COUNT(*) as count,
                lead_owner,
                COUNT(lead_owner) as owner_count
            FROM `tabLead`
            WHERE date(`creation`) between %s and %s
            AND company = %s
            {additional_conditions}
            GROUP BY status, lead_owner
            ORDER BY status, owner_count DESC
        """

        total_data = frappe.db.sql(
            total_leads_query,
            base_filters + tuple(additional_values),
            as_dict=1,
        )

        status_data = frappe.db.sql(
            status_query,
            base_filters + tuple(additional_values),
            as_dict=1,
        )

        total_count = sum(row.count for row in total_data)
        status_counts = {
            "Total Leads": total_count,
            "Connected": 0,
            "Interested": 0,
            "Quotation": 0,
            "Converted": 0,
        }
        owner_details = {status: [] for status in LEAD_STATUSES.keys()}
        owner_details["Total Leads"] = [
            {"owner": row.lead_owner or "Not Assigned", "count": row.owner_count}
            for row in total_data
        ]
        open_enquiry_count = sum(
            row.count for row in status_data if row.status in ["Open", "Enquiry"]
        )
        do_not_contact_count = sum(
            row.count for row in status_data if row.status == "Do Not Contact"
        )
        quotation_count = sum(
            row.count for row in status_data if row.status == "Quotation"
        )
        converted_count = sum(
            row.count for row in status_data if row.status == "Converted"
        )

        status_counts.update(
            {
                "Connected": total_count - open_enquiry_count,
                "Interested": total_count - (open_enquiry_count + do_not_contact_count),
                "Quotation": quotation_count + converted_count,
                "Converted": converted_count,
            }
        )

        for row in status_data:
            if row.status == "Converted":
                owner_details["Converted"].append(
                    {
                        "owner": row.lead_owner or "Not Assigned",
                        "count": row.owner_count,
                    }
                )
                owner_details["Quotation"].append(
                    {
                        "owner": row.lead_owner or "Not Assigned",
                        "count": row.owner_count,
                    }
                )
            elif row.status == "Quotation":
                owner_details["Quotation"].append(
                    {
                        "owner": row.lead_owner or "Not Assigned",
                        "count": row.owner_count,
                    }
                )

        return status_counts, 0, owner_details

    def _prepare_funnel_data(
        self,
        status_counts: dict,
        others_count: int,
        owner_details: dict,
    ) -> list[dict]:
        """
        Prepare final funnel data with owner details for tooltip, sorted by value (descending)
        """

        data = [
            {
                "title": _(status),
                "value": count,
                "color": LEAD_STATUSES[status],
                "owners": owner_details[status],
            }
            for status, count in status_counts.items()
            if count > 0
        ]

        data.sort(key=lambda x: x["value"], reverse=True)

        if others_count:
            data.append(
                {
                    "title": _("Others"),
                    "value": others_count,
                    "color": LEAD_STATUSES["Others"],
                    "owners": owner_details["Others"],
                }
            )

        return data


def get_cache_key(
    from_date: str,
    to_date: str,
    company: str,
    lead_owner: str = None,
    source: str = None,
    department: str = None,
) -> str:
    """Generate a unique cache key based on input parameters"""
    return f"lead_funnel:|{from_date}|{to_date}|{company}|{lead_owner or ''}|{source or ''}|{department or ''}"


@frappe.whitelist()
def get_funnel_data(
    from_date: str,
    to_date: str,
    company: str,
    lead_owner: str | None = None,
    source: str | None = None,
    department: str | None = None,
) -> list[dict]:
    """
    API endpoint to get lead funnel data
    """
    cache_key = get_cache_key(
        from_date, to_date, company, lead_owner, source, department
    )
    funnel_data = frappe.cache().get_value(cache_key)

    if funnel_data is None:
        funnel = LeadFunnel()
        funnel_data = funnel.get_lead_data(
            from_date, to_date, company, lead_owner, source, department
        )
        frappe.cache().set_value(key=cache_key, val=funnel_data, expires_in_sec=30)

    return funnel_data


def clear_cache(
    from_date: str = None,
    to_date: str = None,
    company: str = None,
    lead_owner: str = None,
    source: str = None,
    department: str = None,
) -> None:
    """
    Clear the funnel data cache. If no parameters are provided,
    it will generate a pattern to clear all lead funnel caches.
    """
    if all(
        param is None
        for param in [from_date, to_date, company, lead_owner, source, department]
    ):
        frappe.cache().delete_keys("lead_funnel:*")
    else:
        cache_key = get_cache_key(
            from_date, to_date, company, lead_owner, source, department
        )
        frappe.cache().delete_value(cache_key)
