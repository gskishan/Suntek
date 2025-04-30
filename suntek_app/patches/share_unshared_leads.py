import frappe
from frappe.utils import now_datetime


def execute():
    print("=" * 80)
    print(f"Starting execution at {now_datetime().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    total_count = frappe.db.sql(
        """
        SELECT Count(*) AS count
        FROM   `tabLead`
        WHERE  lead_owner IS NOT NULL
                AND lead_owner != ''
                AND custom_neodove_campaign_name IS NOT NULL
                AND custom_neodove_campaign_name != ''
        """,
        as_dict=1,
    )[0].count

    print(f"Total Neodove leads found: {total_count}")

    if total_count == 0:
        print("No Neodove leads found. Exiting patch.")
        return

    total_shared_count = 0
    total_open_shared = 0
    total_error_count = 0
    total_open_count = 0

    batch_size = 200
    offset = 0
    batch_num = 1

    while offset < total_count:
        print(
            f"Processing batch {batch_num} (leads {offset + 1} to {min(offset + batch_size, total_count)} of {total_count})"
        )

        batch_leads = frappe.db.sql(
            """
            SELECT name,
                   lead_owner,
                   owner,
                   status
            FROM   `tabLead`
            WHERE  lead_owner IS NOT NULL
            AND    lead_owner != ''
            AND    custom_neodove_campaign_name IS NOT NULL
            AND    custom_neodove_campaign_name != ''
            LIMIT  %s
            offset %s
            """,
            (batch_size, offset),
            as_dict=1,
        )

        batch_count = len(batch_leads)
        batch_open_count = sum(1 for lead in batch_leads if lead.status == "Open")
        total_open_count += batch_open_count

        print(f"Batch {batch_num}: {batch_count} leads, {batch_open_count} with status 'Open'")

        open_leads_info = []

        batch_shared = 0
        batch_open_shared = 0
        batch_errors = 0

        for lead in batch_leads:
            try:
                existing_share = frappe.db.exists(
                    "DocShare", {"share_doctype": "Lead", "share_name": lead.name, "user": lead.lead_owner}
                )

                if not existing_share:
                    frappe.share.add(
                        doctype="Lead",
                        name=lead.name,
                        user=lead.lead_owner,
                        read=1,
                        write=1,
                        share=1,
                        notify=0,
                    )
                    batch_shared += 1

                    if lead.status == "Open":
                        batch_open_shared += 1
                        open_leads_info.append(f"{lead.name} - Owner: {lead.lead_owner}")

            except Exception as e:
                batch_errors += 1
                error_msg = f"Error sharing lead {lead.name} with {lead.lead_owner} [Status: {lead.status}]: {str(e)}"
                print(error_msg)
                frappe.log_error(error_msg, "Neodove Lead Sharing Patch Error")

        if open_leads_info:
            print(f"\nOpen leads newly shared in batch {batch_num}:")
            for info in open_leads_info:
                print(f"  - {info}")
            print("")

        total_shared_count += batch_shared
        total_open_shared += batch_open_shared
        total_error_count += batch_errors

        frappe.db.commit()
        print(
            f"Batch {batch_num} complete: {batch_shared} leads shared ({batch_open_shared} open), {batch_errors} errors"
        )
        print("-" * 40)

        offset += batch_size
        batch_num += 1

    print("=" * 80)
    print(f"PATCH COMPLETE at {now_datetime().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Neodove leads processed: {total_count}")
    print(f"Total leads with status 'Open': {total_open_count}")
    print(f"Errors encountered: {total_error_count}")
    print("=" * 80)

    frappe.log_error(
        title="Neodove Lead Sharing Fixed",
        message=f"""
        Fixed critical visibility issue: {total_shared_count} Neodove leads were previously invisible to their owners.
        {total_open_shared} of these were OPEN leads that may require urgent follow-up.
        Total Neodove leads: {total_count} (Open: {total_open_count}).
        """,
    )
