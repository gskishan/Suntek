# suntek/suntek/doctype/lead_funnel/lead_funnel.py

import frappe
from frappe import _
from typing import Dict, List, Optional, Tuple

LEAD_STATUSES = {
    "Open": "#2E86C1",  # Strong blue - beginning of funnel
    "Lead": "#3498DB",  # Lighter blue - early stage
    "Replied": "#1ABC9C",  # Turquoise - showing engagement
    "Interested": "#F1C40F",  # Yellow - warming up
    "Opportunity": "#E67E22",  # Orange - getting warmer
    "Quotation": "#D35400",  # Deep orange - close to conversion
    "Converted": "#27AE60",  # Green - success
    "Lost": "#E74C3C",  # Red - negative outcome
    "Do Not Contact": "#95A5A6",  # Gray - neutral/inactive
    "Others": "#7F8C8D",  # Darker gray - miscellaneous
}


class LeadFunnel:
    def __init__(self):
        self.filters = {}

    def get_lead_data(self, from_date: str, to_date: str, company: str, lead_owner: Optional[str] = None, source: Optional[str] = None) -> List[Dict]:
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
        return (from_date, to_date, company)

    def _get_additional_filters(self, lead_owner: Optional[str], source: Optional[str]) -> Tuple[str, List]:
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

    def _get_lead_counts(self, base_filters: Tuple, additional_conditions: str, additional_values: List) -> Tuple[Dict, int, Dict]:
        """
        Get lead counts and owner details for each status
        """
        main_statuses = tuple(LEAD_STATUSES.keys() - {"Others"})

        # Query for main statuses with owner details
        status_data = frappe.db.sql(
            """
            SELECT 
                status,
                COUNT(*) as count,
                lead_owner,
                COUNT(lead_owner) as owner_count
            FROM `tabLead`
            WHERE status IN %s 
            AND (date(`creation`) between %s and %s)
            AND company = %s
            {0}
            GROUP BY status, lead_owner
            ORDER BY status, owner_count DESC
            """.format(
                additional_conditions
            ),
            (main_statuses,) + base_filters + tuple(additional_values),
            as_dict=1,
        )

        # Process main status results
        status_counts = {}
        owner_details = {}

        for row in status_data:
            status = row.status
            if status not in status_counts:
                status_counts[status] = 0
                owner_details[status] = []

            status_counts[status] += row.count
            owner_details[status].append({"owner": row.lead_owner or "Not Assigned", "count": row.owner_count})

        # Query for other statuses
        others_data = frappe.db.sql(
            """
            SELECT 
                COUNT(*) as count,
                lead_owner,
                COUNT(lead_owner) as owner_count
            FROM `tabLead`
            WHERE status NOT IN %s
            AND (date(`creation`) between %s and %s)
            AND company = %s
            {0}
            GROUP BY lead_owner
            ORDER BY owner_count DESC
            """.format(
                additional_conditions
            ),
            (main_statuses,) + base_filters + tuple(additional_values),
            as_dict=1,
        )

        others_count = sum(row.count for row in others_data)
        owner_details["Others"] = [{"owner": row.lead_owner or "Not Assigned", "count": row.owner_count} for row in others_data]

        return status_counts, others_count, owner_details

    def _prepare_funnel_data(self, status_counts: Dict, others_count: int, owner_details: Dict) -> List[Dict]:
        """
        Prepare final funnel data with owner details for tooltip, sorted by value (descending)
        """
        # Create data list and sort by value in descending order
        data = [
            {"title": _(status), "value": count, "color": LEAD_STATUSES[status], "owners": owner_details[status]}
            for status, count in status_counts.items()
            if count > 0
        ]

        # Sort data by value in descending order
        data.sort(key=lambda x: x["value"], reverse=True)

        # Add others category at the end if it exists
        if others_count:
            data.append({"title": _("Others"), "value": others_count, "color": LEAD_STATUSES["Others"], "owners": owner_details["Others"]})

        return data


@frappe.whitelist()
def get_funnel_data(from_date: str, to_date: str, company: str, lead_owner: Optional[str] = None, source: Optional[str] = None) -> List[Dict]:
    """
    API endpoint to get lead funnel data
    """
    funnel = LeadFunnel()
    return funnel.get_lead_data(from_date, to_date, company, lead_owner, source)
