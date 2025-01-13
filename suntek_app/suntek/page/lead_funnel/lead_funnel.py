from typing import Dict, List, Optional

import frappe
from frappe import _

LEAD_STATUSES = {
    "Open": "#2C9BC8",
    "Interested": "#4CAF50",
    "Quotation": "#9C27B0",
    "Converted": "#28A745",
    "Do Not Contact": "#DC3545",
    "Others": "#FD7E14",
}

CACHE_TTL = 300  # 5 minutes


def validate_filters(from_date: str, to_date: str, company: str) -> None:
    """Validate input filters for the funnel data query."""
    if from_date and to_date and (from_date >= to_date):
        frappe.throw(_("To Date must be greater than From Date"))
    if not company:
        frappe.throw(_("Please Select a Company"))


def build_conditions(lead_owner: Optional[str] = None, source: Optional[str] = None) -> tuple:
    """Build SQL conditions and values for filtering."""
    conditions = []
    values = []

    if lead_owner:
        conditions.append("lead_owner = %s")
        values.append(lead_owner)

    if source:
        conditions.append("source = %s")
        values.append(source)

    return (" AND " + " AND ".join(conditions)) if conditions else "", values


def get_lead_counts(base_filters: tuple, additional_conditions: str, additional_values: List) -> Dict:
    """Get counts for each lead status."""
    main_statuses = tuple(LEAD_STATUSES.keys() - {"Others"})

    # Get counts for other statuses in a single query
    others_count = frappe.db.sql(
        """
        SELECT COUNT(*) as count 
        FROM `tabLead` 
        WHERE status NOT IN %s
        AND (date(`creation`) between %s and %s)
        AND company = %s
        {}
    """.format(
            additional_conditions
        ),
        (main_statuses,) + base_filters + tuple(additional_values),
    )[0][0]

    # Get counts for main statuses in a single query
    status_counts = frappe.db.sql(
        """
        SELECT status, COUNT(*) as count 
        FROM `tabLead`
        WHERE status IN %s 
        AND (date(`creation`) between %s and %s)
        AND company = %s
        {}
        GROUP BY status
    """.format(
            additional_conditions
        ),
        (main_statuses,) + base_filters + tuple(additional_values),
    )

    return dict(status_counts), others_count


def get_cache_key(from_date: str, to_date: str, company: str, lead_owner: Optional[str] = None, source: Optional[str] = None) -> str:
    """Generate a unique cache key based on parameters"""
    key_parts = ["lead_funnel", f"from_{from_date}", f"to_{to_date}", f"company_{company}"]
    if lead_owner:
        key_parts.append(f"owner_{lead_owner}")
    if source:
        key_parts.append(f"source_{source}")
    return ":".join(key_parts)


@frappe.whitelist()
def get_funnel_data(from_date: str, to_date: str, company: str, lead_owner: Optional[str] = None, source: Optional[str] = None) -> List[Dict]:
    """Get funnel data for leads with improved caching."""

    # Generate cache key
    cache_key = get_cache_key(from_date, to_date, company, lead_owner, source)

    try:
        # Attempt to get cached data
        cached_data = frappe.cache().get_value(cache_key)
        if cached_data:
            return cached_data

        # Validate filters
        validate_filters(from_date, to_date, company)

        # Get fresh data
        additional_conditions, additional_values = build_conditions(lead_owner, source)
        base_filters = (from_date, to_date, company)
        status_counts, others_count = get_lead_counts(base_filters, additional_conditions, additional_values)

        # Prepare response data
        data = [{"title": _(status), "value": count, "color": LEAD_STATUSES[status]} for status, count in status_counts.items() if count > 0]

        if others_count:
            data.append({"title": _("Others"), "value": others_count, "color": LEAD_STATUSES["Others"]})

        # Cache the results
        frappe.cache().set_value(key=cache_key, val=data, expires_in_sec=CACHE_TTL)

        return data

    except Exception as e:
        frappe.log_error(f"Lead Funnel Error: {str(e)}", "get_funnel_data")
        raise


def clear_lead_funnel_cache() -> None:
    """Clear all lead funnel related caches"""
    keys = frappe.cache().get_keys("lead_funnel*")
    for key in keys:
        frappe.cache().delete_value(key)
