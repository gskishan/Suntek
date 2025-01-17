from typing import Dict, List, Optional, Tuple

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
        lead_owner: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get lead funnel data with owner details for tooltip
        """
        base_filters = self._get_base_filters(from_date, to_date, company)
        additional_conditions, additional_values = self._get_additional_filters(lead_owner, source)
        status_counts, others_count, owner_details = self._get_lead_counts(base_filters, additional_conditions, additional_values)

        return self._prepare_funnel_data(status_counts, others_count, owner_details)

    def _get_base_filters(self, from_date: str, to_date: str, company: str) -> Tuple:
        """
        Prepare base filters for lead query
        """
        return (from_date, to_date, from_date, to_date, company)

    def _get_additional_filters(
        self,
        lead_owner: Optional[str],
        source: Optional[str],
    ) -> Tuple[str, List]:
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

        additional_conditions = f"AND {' AND '.join(conditions)}" if conditions else ""

        return additional_conditions, values

    def _get_lead_counts(
        self,
        base_filters: Tuple,
        additional_conditions: str,
        additional_values: List,
    ) -> Tuple[Dict, int, Dict]:
        """
        Get lead counts and owner details for each stage
        """

        total_leads_query = """
            SELECT 
                COUNT(*) as count,
                lead_owner,
                COUNT(lead_owner) as owner_count
            FROM `tabLead`
            WHERE (date(`creation`) between %s and %s 
                OR date(`modified`) between %s and %s)
            AND company = %s
            {0}
            GROUP BY lead_owner
            ORDER BY owner_count DESC
        """.format(
            additional_conditions
        )

        total_data = frappe.db.sql(
            total_leads_query,
            base_filters + tuple(additional_values),
            as_dict=1,
        )

        status_query = """
            SELECT 
                status,
                COUNT(*) as count,
                lead_owner,
                COUNT(lead_owner) as owner_count
            FROM `tabLead`
            WHERE (date(`creation`) between %s and %s 
                OR date(`modified`) between %s and %s)
            AND company = %s
            {0}
            GROUP BY status, lead_owner
            ORDER BY status, owner_count DESC
        """.format(
            additional_conditions
        )

        status_data = frappe.db.sql(
            status_query,
            base_filters + tuple(additional_values),
            as_dict=1,
        )

        total_count = sum(row.count for row in total_data)
        status_counts = {"Total Leads": total_count, "Connected": 0, "Interested": 0, "Quotation": 0, "Converted": 0}
        owner_details = {status: [] for status in LEAD_STATUSES.keys()}
        owner_details["Total Leads"] = [{"owner": row.lead_owner or "Not Assigned", "count": row.owner_count} for row in total_data]
        open_enquiry_count = sum(row.count for row in status_data if row.status in ["Open", "Enquiry"])
        do_not_contact_count = sum(row.count for row in status_data if row.status == "Do Not Contact")
        quotation_count = sum(row.count for row in status_data if row.status == "Quotation")
        converted_count = sum(row.count for row in status_data if row.status == "Converted")

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
                owner_details["Converted"].append({"owner": row.lead_owner or "Not Assigned", "count": row.owner_count})
                owner_details["Quotation"].append({"owner": row.lead_owner or "Not Assigned", "count": row.owner_count})
            elif row.status == "Quotation":
                owner_details["Quotation"].append({"owner": row.lead_owner or "Not Assigned", "count": row.owner_count})

        return status_counts, 0, owner_details

    def _prepare_funnel_data(
        self,
        status_counts: Dict,
        others_count: int,
        owner_details: Dict,
    ) -> List[Dict]:
        """
        Prepare final funnel data with owner details for tooltip, sorted by value (descending)
        """

        data = [
            {"title": _(status), "value": count, "color": LEAD_STATUSES[status], "owners": owner_details[status]}
            for status, count in status_counts.items()
            if count > 0
        ]

        data.sort(key=lambda x: x["value"], reverse=True)

        if others_count:
            data.append({"title": _("Others"), "value": others_count, "color": LEAD_STATUSES["Others"], "owners": owner_details["Others"]})

        return data


@frappe.whitelist()
def get_funnel_data(
    from_date: str,
    to_date: str,
    company: str,
    lead_owner: Optional[str] = None,
    source: Optional[str] = None,
) -> List[Dict]:
    """
    API endpoint to get lead funnel data
    """
    funnel = LeadFunnel()
    return funnel.get_lead_data(from_date, to_date, company, lead_owner, source)
