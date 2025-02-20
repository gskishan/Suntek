import frappe


def add_enquiry_to_links(doc, method=None):
    opp_link = None
    for link in doc.links:
        if link.link_doctype == "Opportunity":
            opp_link = link
            break
    if not opp_link:
        return

    opp = frappe.get_value("Opportunity", opp_link.link_name, ["party_name"], as_dict=1)

    if not opp.party_name:
        return

    for link in doc.links:
        if link.link_doctype == "Lead" and link.link_name == opp.party_name:
            return

    doc.append(
        "links",
        {
            "link_doctype": "Lead",
            "link_name": opp.party_name,
            "link_title": opp_link.link_title,
        },
    )
