import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "lead_id", "label": _("Lead ID"), "fieldtype": "Link", "options": "Lead", "width": 110},
        {"fieldname": "lead_created_month", "label": _("Lead Created Month"), "fieldtype": "Data", "width": 140},
        {"fieldname": "full_name", "label": _("Full Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "lead_owner", "label": _("Lead Owner"), "fieldtype": "Data", "width": 140},
        {"fieldname": "lead_source", "label": _("Lead Source"), "fieldtype": "Data", "width": 120},
        {
            "fieldname": "opportunity_id",
            "label": _("Opportunity ID"),
            "fieldtype": "Link",
            "options": "Opportunity",
            "width": 140,
        },
        {
            "fieldname": "opportunity_created_date",
            "label": _("Opportunity Created Date"),
            "fieldtype": "Date",
            "width": 160,
        },
        {"fieldname": "opportunity_owner", "label": _("Opportunity Owner"), "fieldtype": "Data", "width": 150},
        {"fieldname": "opportunity_source", "label": _("Source"), "fieldtype": "Data", "width": 120},
        {"fieldname": "sales_executive", "label": _("Field Sales Executive"), "fieldtype": "Data", "width": 180},
        {"fieldname": "type_of_case", "label": _("Type of Case"), "fieldtype": "Data", "width": 120},
        {"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "mobile_no", "label": _("Mobile No"), "fieldtype": "Data", "width": 120},
        {"fieldname": "customer_category", "label": _("Customer Category"), "fieldtype": "Data", "width": 150},
        {"fieldname": "state", "label": _("State"), "fieldtype": "Data", "width": 120},
        {"fieldname": "branch", "label": _("Branch"), "fieldtype": "Data", "width": 120},
        {
            "fieldname": "site_survey_id",
            "label": _("Site Survey ID"),
            "fieldtype": "Link",
            "options": "Site Survey",
            "width": 130,
        },
        {"fieldname": "site_survey_date", "label": _("Site Survey Date"), "fieldtype": "Date", "width": 140},
        {"fieldname": "site_visited_by", "label": _("Site Visited By"), "fieldtype": "Data", "width": 150},
        {
            "fieldname": "quotation_id",
            "label": _("Quotation ID"),
            "fieldtype": "Link",
            "options": "Quotation",
            "width": 130,
        },
        {"fieldname": "quotation_date", "label": _("Quotation Creation Date"), "fieldtype": "Date", "width": 180},
        {"fieldname": "capacity", "label": _("Capacity"), "fieldtype": "Data", "width": 100},
        {"fieldname": "final_price", "label": _("Final Price"), "fieldtype": "Currency", "width": 120},
        {
            "fieldname": "sales_order_id",
            "label": _("Sales Order ID"),
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 130,
        },
        {"fieldname": "sales_order_date", "label": _("Sales Order Creation Date"), "fieldtype": "Date", "width": 180},
        {
            "fieldname": "sales_order_created_by",
            "label": _("Sales Order Created By"),
            "fieldtype": "Data",
            "width": 170,
        },
        {"fieldname": "delivery_date", "label": _("Delivery Date"), "fieldtype": "Date", "width": 130},
        {"fieldname": "sales_order_value", "label": _("Sales Order Value"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "order_type", "label": _("Order Type"), "fieldtype": "Data", "width": 120},
        {"fieldname": "structure_height", "label": _("Structure Height"), "fieldtype": "Data", "width": 140},
        {"fieldname": "project_id", "label": _("Project ID"), "fieldtype": "Link", "options": "Project", "width": 110},
        {"fieldname": "design_id", "label": _("Design ID"), "fieldtype": "Link", "options": "Designing", "width": 110},
        {"fieldname": "design_date", "label": _("Design Creation Date"), "fieldtype": "Date", "width": 160},
        {"fieldname": "design_created_by", "label": _("Design Created By"), "fieldtype": "Data", "width": 150},
        {"fieldname": "bom_id", "label": _("BOM ID"), "fieldtype": "Link", "options": "BOM", "width": 110},
        {
            "fieldname": "work_order_id",
            "label": _("Work Order ID"),
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 130,
        },
        {"fieldname": "work_order_date", "label": _("Work Order Creation Date"), "fieldtype": "Date", "width": 180},
        {
            "fieldname": "work_order_completion_date",
            "label": _("Work Order Completion Date"),
            "fieldtype": "Date",
            "width": 200,
        },
        {
            "fieldname": "delivery_note_id",
            "label": _("Delivery Note ID"),
            "fieldtype": "Link",
            "options": "Delivery Note",
            "width": 140,
        },
        {
            "fieldname": "delivery_note_date",
            "label": _("Delivery Note Creation Date"),
            "fieldtype": "Date",
            "width": 200,
        },
        {
            "fieldname": "sales_invoice_id",
            "label": _("Sales Invoice ID"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 140,
        },
        {"fieldname": "sales_invoice_date", "label": _("Sales Invoice Date"), "fieldtype": "Date", "width": 150},
        {"fieldname": "ewaybill_no", "label": _("e-waybill No."), "fieldtype": "Data", "width": 140},
        {
            "fieldname": "ewaybill_generation_date",
            "label": _("e-waybill Generation Date"),
            "fieldtype": "Date",
            "width": 200,
        },
        {
            "fieldname": "installation_note_id",
            "label": _("Installation Note ID"),
            "fieldtype": "Link",
            "options": "Installation Note",
            "width": 160,
        },
        {
            "fieldname": "installation_note_date",
            "label": _("Installation Note Creation Date"),
            "fieldtype": "Date",
            "width": 210,
        },
        {"fieldname": "installation_remarks", "label": _("Installation Remarks"), "fieldtype": "Data", "width": 160},
        {"fieldname": "discom_status", "label": _("Discom Status"), "fieldtype": "Data", "width": 130},
        {"fieldname": "load_enhancement", "label": _("Load Enhancement"), "fieldtype": "Data", "width": 150},
        {"fieldname": "load_number", "label": _("Load Number"), "fieldtype": "Data", "width": 130},
        {"fieldname": "meter_draw_date", "label": _("Meter Draw Date"), "fieldtype": "Date", "width": 140},
        {"fieldname": "meter_fitting_date", "label": _("Meter Fitting Date"), "fieldtype": "Date", "width": 150},
        {"fieldname": "synchronization_date", "label": _("Synchronization Date"), "fieldtype": "Date", "width": 160},
        {"fieldname": "done_by", "label": _("Done By"), "fieldtype": "Data", "width": 120},
        {"fieldname": "pcr_date", "label": _("PCR Date"), "fieldtype": "Date", "width": 120},
        {"fieldname": "subsidy_status", "label": _("Subsidy Status"), "fieldtype": "Data", "width": 130},
        {
            "fieldname": "subsidy_amt_received_date",
            "label": _("Subsidy Amt Received Date"),
            "fieldtype": "Date",
            "width": 190,
        },
        {"fieldname": "subsidy_amount", "label": _("Subsidy Amount"), "fieldtype": "Currency", "width": 140},
    ]


def get_data(filters):
    data = []

    leads = get_leads(filters)

    for lead in leads:
        row = {
            "lead_id": lead.name,
            "lead_created_month": lead.creation.strftime("%B %Y") if lead.creation else "N/A",
            "full_name": f"{lead.first_name or ''} {lead.last_name or ''}".strip(),
            "lead_owner": lead.lead_owner,
            "lead_source": lead.source,
            "opportunity_id": "N/A",
            "opportunity_created_date": "N/A",
            "opportunity_owner": "N/A",
            "opportunity_source": "N/A",
            "sales_executive": "N/A",
            "type_of_case": "N/A",
            "customer_name": "N/A",
            "mobile_no": lead.mobile_no,
            "customer_category": "N/A",
            "state": lead.custom_suntek_state if hasattr(lead, "custom_suntek_state") else "N/A",
            "branch": "N/A",
        }

        opportunity = get_opportunity_from_lead(lead.name, filters)
        if opportunity:
            update_row_with_opportunity(row, opportunity)

            if not meets_opportunity_filters(row, filters):
                continue

            site_survey = get_site_survey_from_opportunity(opportunity.name)
            if site_survey:
                update_row_with_site_survey(row, site_survey)

            quotation = get_quotation_from_opportunity(opportunity.name)
            if quotation:
                update_row_with_quotation(row, quotation)

                sales_order = get_sales_order_from_quotation(quotation.name)
                if sales_order:
                    update_row_with_sales_order(row, sales_order)

                    project = get_project_from_sales_order(sales_order.name)
                    if project:
                        update_row_with_project(row, project)

                        discom = get_discom_from_project(project.name)
                        if discom:
                            update_row_with_discom(row, discom)

                        subsidy = get_subsidy_from_project(project.name)
                        if subsidy:
                            update_row_with_subsidy(row, subsidy)

                    design = get_design_from_sales_order_or_project(sales_order.name, row.get("project_id", ""))
                    if design:
                        update_row_with_design(row, design)

                    bom = get_bom_from_sales_order_or_project(sales_order.name, row.get("project_id", ""))
                    if bom:
                        update_row_with_bom(row, bom)

                        work_order = get_work_order_from_bom(bom.name)
                        if work_order:
                            update_row_with_work_order(row, work_order)

                    delivery_note = get_delivery_note_from_sales_order(sales_order.name)
                    if delivery_note:
                        update_row_with_delivery_note(row, delivery_note)

                    sales_invoice = get_sales_invoice_from_sales_order(sales_order.name)
                    if sales_invoice:
                        update_row_with_sales_invoice(row, sales_invoice)

                    installation_note = get_installation_note_from_sales_order(sales_order.name)
                    if installation_note:
                        update_row_with_installation_note(row, installation_note)

        data.append(row)

    return data


def meets_opportunity_filters(row, filters):
    if not filters:
        return True

    if filters.get("customer_category") and row.get("customer_category") != filters.get("customer_category"):
        return False

    if filters.get("type_of_case") and row.get("type_of_case") != filters.get("type_of_case"):
        return False

    if filters.get("sales_executive") and row.get("sales_executive") != filters.get("sales_executive"):
        return False

    if filters.get("branch") and row.get("branch") != filters.get("branch"):
        return False

    return True


def get_leads(filters):
    conditions = ""
    values = {}

    if filters:
        if filters.get("from_date"):
            conditions += " AND l.creation >= %(from_date)s"
            values["from_date"] = filters.get("from_date")

        if filters.get("to_date"):
            conditions += " AND l.creation <= %(to_date)s"
            values["to_date"] = filters.get("to_date")

        if filters.get("lead_owner"):
            conditions += " AND l.lead_owner = %(lead_owner)s"
            values["lead_owner"] = filters.get("lead_owner")

        if filters.get("source"):
            conditions += " AND l.source = %(source)s"
            values["source"] = filters.get("source")

        if filters.get("state"):
            conditions += " AND l.custom_suntek_state = %(state)s"
            values["state"] = filters.get("state")

    leads = frappe.db.sql(
        f"""
        SELECT
            l.name, l.creation, l.first_name, l.last_name, l.lead_owner,
            l.source, l.mobile_no, l.custom_suntek_state
        FROM
            `tabLead` l
        WHERE
            l.docstatus < 2 {conditions}
        ORDER BY
            l.creation DESC
    """,
        values,
        as_dict=True,
    )

    return leads


def get_opportunity_from_lead(lead_id, filters=None):
    conditions = " AND o.opportunity_from = 'Lead' AND o.party_name = %s AND o.docstatus < 2"
    values = [lead_id]

    if filters:
        if filters.get("customer_category"):
            conditions += " AND o.custom_customer_category = %s"
            values.append(filters.get("customer_category"))

        if filters.get("type_of_case"):
            conditions += " AND o.custom_type_of_case = %s"
            values.append(filters.get("type_of_case"))

        if filters.get("sales_executive"):
            conditions += " AND o.custom_sales_excecutive = %s"
            values.append(filters.get("sales_executive"))

        if filters.get("branch"):
            conditions += " AND o.custom_branch = %s"
            values.append(filters.get("branch"))

    opportunities = frappe.db.sql(
        f"""
        SELECT
            o.name, o.creation, o.opportunity_owner, o.source,
            o.custom_sales_excecutive, o.custom_type_of_case,
            o.custom_customer_category, o.custom_suntek_state, o.custom_branch,
            CASE
                WHEN o.custom_customer_category = 'Individual' THEN o.contact_person
                WHEN o.custom_customer_category = 'C & I' THEN o.custom_company_name
                ELSE o.customer_name
            END as customer_name,
            o.contact_mobile
        FROM
            `tabOpportunity` o
        WHERE
            1=1 {conditions}
        ORDER BY
            o.creation DESC
        LIMIT 1
    """,
        values,
        as_dict=True,
    )

    return opportunities[0] if opportunities else None


def get_site_survey_from_opportunity(opportunity_id):
    site_surveys = frappe.db.sql(
        """
        SELECT
            ss.name, ss.creation, ss.custom_site_visitor
        FROM
            `tabSite Survey` ss
        WHERE
            ss.opportunity_name = %s
            AND ss.docstatus < 2
        ORDER BY
            ss.creation DESC
        LIMIT 1
    """,
        opportunity_id,
        as_dict=True,
    )

    return site_surveys[0] if site_surveys else None


def get_quotation_from_opportunity(opportunity_id):
    quotations = frappe.db.sql(
        """
        SELECT
            q.name, q.creation, q.custom_capacity, q.grand_total
        FROM
            `tabQuotation` q
        WHERE
            q.opportunity = %s
            AND q.docstatus < 2
        ORDER BY
            q.creation DESC
        LIMIT 1
    """,
        opportunity_id,
        as_dict=True,
    )

    return quotations[0] if quotations else None


def get_sales_order_from_quotation(quotation_id):
    sales_orders = frappe.db.sql(
        """
        SELECT
            so.name, so.creation, so.owner, so.delivery_date,
            so.grand_total, so.order_type, so.custom_height
        FROM
            `tabSales Order` so
        WHERE
            so.name IN (
                SELECT parent FROM `tabSales Order Item`
                WHERE prevdoc_docname = %s
            )
            AND so.docstatus < 2
        ORDER BY
            so.creation DESC
        LIMIT 1
    """,
        quotation_id,
        as_dict=True,
    )

    return sales_orders[0] if sales_orders else None


def get_project_from_sales_order(sales_order_id):
    projects = frappe.db.sql(
        """
        SELECT
            p.name, p.creation
        FROM
            `tabProject` p
        WHERE
            p.sales_order = %s
            AND p.docstatus < 2
        LIMIT 1
    """,
        sales_order_id,
        as_dict=True,
    )

    return projects[0] if projects else None


def get_design_from_sales_order_or_project(sales_order_id, project_id):
    conditions = []
    params = []

    if project_id and project_id != "N/A":
        conditions.append("d.custom_project = %s")
        params.append(project_id)

    if not conditions and sales_order_id and sales_order_id != "N/A":
        opportunity_name = None
        opportunity = frappe.db.sql(
            """
            SELECT so.custom_opportunity_name
            FROM `tabSales Order` so
            WHERE so.name = %s
        """,
            sales_order_id,
            as_dict=True,
        )

        if opportunity and opportunity[0].custom_opportunity_name:
            opportunity_name = opportunity[0].custom_opportunity_name
            conditions.append("d.opportunity_name = %s")
            params.append(opportunity_name)

    if not conditions:
        return None

    designs = frappe.db.sql(
        """
        SELECT
            d.name, d.creation, d.designer as created_by
        FROM
            `tabDesigning` d
        WHERE
            ({})
            AND d.docstatus < 2
        ORDER BY
            d.creation DESC
        LIMIT 1
    """.format(" OR ".join(conditions)),
        params,
        as_dict=True,
    )

    return designs[0] if designs else None


def get_bom_from_sales_order_or_project(sales_order_id, project_id):
    conditions = []
    params = []

    if project_id and project_id != "N/A":
        conditions.append("b.project = %s")
        params.append(project_id)

    if not conditions and sales_order_id and sales_order_id != "N/A":
        try:
            has_sales_order_field = frappe.db.sql("""
                SELECT 1
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'tabBOM'
                AND COLUMN_NAME = 'sales_order'
            """)

            if has_sales_order_field:
                conditions.append("b.sales_order = %s")
                params.append(sales_order_id)
            else:
                boms = frappe.db.sql(
                    """
                    SELECT DISTINCT b.name
                    FROM `tabBOM` b
                    JOIN `tabBOM Item` bi ON b.name = bi.parent
                    JOIN `tabSales Order Item` soi ON bi.item_code = soi.item_code
                    WHERE soi.parent = %s
                """,
                    sales_order_id,
                )

                if boms:
                    conditions.append("b.name = %s")
                    params.append(boms[0][0])
        except Exception:
            pass

    if not conditions:
        return None

    boms = frappe.db.sql(
        """
        SELECT
            b.name, b.creation
        FROM
            `tabBOM` b
        WHERE
            ({})
            AND b.docstatus < 2
        ORDER BY
            b.creation DESC
        LIMIT 1
    """.format(" OR ".join(conditions)),
        params,
        as_dict=True,
    )

    return boms[0] if boms else None


def get_work_order_from_bom(bom_id):
    work_orders = frappe.db.sql(
        """
        SELECT
            wo.name, wo.creation, wo.actual_end_date as completion_date
        FROM
            `tabWork Order` wo
        WHERE
            wo.bom_no = %s
            AND wo.docstatus < 2
        ORDER BY
            wo.creation DESC
        LIMIT 1
    """,
        bom_id,
        as_dict=True,
    )

    return work_orders[0] if work_orders else None


def get_delivery_note_from_sales_order(sales_order_id):
    project = frappe.db.get_value("Project", {"sales_order": sales_order_id}, "name")

    if not project:
        return None

    delivery_notes = frappe.db.sql(
        """
        SELECT
            dn.name, dn.creation
        FROM
            `tabDelivery Note` dn
        WHERE
            dn.project = %s
            AND dn.docstatus < 2
        ORDER BY
            dn.creation DESC
        LIMIT 1
    """,
        project,
        as_dict=True,
    )

    if not delivery_notes:
        delivery_notes = frappe.db.sql(
            """
            SELECT
                dn.name, dn.creation
            FROM
                `tabDelivery Note` dn
            WHERE
                dn.name IN (
                    SELECT parent FROM `tabDelivery Note Item`
                    WHERE against_sales_order = %s
                )
                AND dn.docstatus < 2
            ORDER BY
                dn.creation DESC
            LIMIT 1
        """,
            sales_order_id,
            as_dict=True,
        )

    return delivery_notes[0] if delivery_notes else None


def get_sales_invoice_from_sales_order(sales_order_id):
    sales_invoices = frappe.db.sql(
        """
        SELECT
            si.name, si.creation, si.posting_date, si.ewaybill
        FROM
            `tabSales Invoice` si
        WHERE
            si.name IN (
                SELECT parent FROM `tabSales Invoice Item`
                WHERE sales_order = %s
            )
            AND si.docstatus < 2
        ORDER BY
            si.creation DESC
        LIMIT 1
    """,
        sales_order_id,
        as_dict=True,
    )

    invoice = sales_invoices[0] if sales_invoices else None

    if invoice and invoice.ewaybill:
        ewaybill_log = frappe.db.sql(
            """
            SELECT creation
            FROM `tabe-Waybill Log`
            WHERE reference_name = %s
            ORDER BY creation ASC
            LIMIT 1
        """,
            invoice.name,
            as_dict=True,
        )

        if ewaybill_log:
            invoice.ewaybill_date = ewaybill_log[0].creation

    return invoice


def get_installation_note_from_sales_order(sales_order_id):
    project = frappe.db.get_value("Project", {"sales_order": sales_order_id}, "name")

    if not project:
        return None

    installation_notes = frappe.db.sql(
        """
        SELECT
            inst_note.name, inst_note.creation, inst_note.remarks
        FROM
            `tabInstallation Note` inst_note
        WHERE
            inst_note.custom_project = %s
            AND inst_note.docstatus < 2
        ORDER BY
            inst_note.creation DESC
        LIMIT 1
    """,
        project,
        as_dict=True,
    )

    return installation_notes[0] if installation_notes else None


def get_discom_from_project(project_id):
    query = """
        SELECT
            d.name, d.discom_status as discom_status, d.custom_load_enhancement,
            d.custom_load_number, d.meter_drawn_date, d.meter_fitting_date,
            d.custom_synchronization_report_date_48hr as synchronization_date
        FROM
            `tabDiscom` d
        WHERE
            d.project_name = %s
            AND d.docstatus < 2
        ORDER BY
            d.creation DESC
        LIMIT 1
    """

    discoms = frappe.db.sql(query, project_id, as_dict=True)

    return discoms[0] if discoms else None


def get_subsidy_from_project(project_id):
    query = """
        SELECT
            s.name, s.pcr_submit_date, s.subsidy_status,
            s.subsidy_cheque_date, s.custom_subsidy_amount
        FROM
            `tabSubsidy` s
        WHERE
            s.project_name = %s
            AND s.docstatus < 2
        ORDER BY
            s.creation DESC
        LIMIT 1
    """

    subsidies = frappe.db.sql(query, project_id, as_dict=True)

    return subsidies[0] if subsidies else None


def update_row_with_opportunity(row, opportunity):
    row.update(
        {
            "opportunity_id": opportunity.name,
            "opportunity_created_date": opportunity.creation.date() if opportunity.creation else "N/A",
            "opportunity_owner": opportunity.opportunity_owner or "N/A",
            "opportunity_source": opportunity.source or "N/A",
            "sales_executive": opportunity.custom_sales_excecutive or "N/A",
            "type_of_case": opportunity.custom_type_of_case or "N/A",
            "customer_name": opportunity.customer_name or "N/A",
            "mobile_no": opportunity.contact_mobile or row.get("mobile_no", "N/A"),
            "customer_category": opportunity.custom_customer_category or "N/A",
            "state": opportunity.custom_suntek_state or row.get("state", "N/A"),
            "branch": opportunity.custom_branch or row.get("branch", "N/A"),
        }
    )


def update_row_with_site_survey(row, site_survey):
    row.update(
        {
            "site_survey_id": site_survey.name,
            "site_survey_date": site_survey.creation.date() if site_survey.creation else "N/A",
            "site_visited_by": site_survey.custom_site_visitor or "N/A",
        }
    )


def update_row_with_quotation(row, quotation):
    row.update(
        {
            "quotation_id": quotation.name,
            "quotation_date": quotation.creation.date() if quotation.creation else "N/A",
            "capacity": quotation.custom_capacity or "N/A",
            "final_price": quotation.grand_total or 0,
        }
    )


def update_row_with_sales_order(row, sales_order):
    row.update(
        {
            "sales_order_id": sales_order.name,
            "sales_order_date": sales_order.creation.date() if sales_order.creation else "N/A",
            "sales_order_created_by": sales_order.owner or "N/A",
            "delivery_date": sales_order.delivery_date or "N/A",
            "sales_order_value": sales_order.grand_total or 0,
            "order_type": sales_order.order_type or "N/A",
            "structure_height": sales_order.custom_height or "N/A",
        }
    )


def update_row_with_project(row, project):
    row.update(
        {
            "project_id": project.name,
        }
    )


def update_row_with_design(row, design):
    row.update(
        {
            "design_id": design.name,
            "design_date": design.creation.date() if design.creation else "N/A",
            "design_created_by": design.created_by or "N/A",
        }
    )


def update_row_with_bom(row, bom):
    row.update(
        {
            "bom_id": bom.name,
        }
    )


def update_row_with_work_order(row, work_order):
    row.update(
        {
            "work_order_id": work_order.name,
            "work_order_date": work_order.creation.date() if work_order.creation else "N/A",
            "work_order_completion_date": work_order.completion_date or "N/A",
        }
    )


def update_row_with_delivery_note(row, delivery_note):
    row.update(
        {
            "delivery_note_id": delivery_note.name,
            "delivery_note_date": delivery_note.creation.date() if delivery_note.creation else "N/A",
        }
    )


def update_row_with_sales_invoice(row, sales_invoice):
    row.update(
        {
            "sales_invoice_id": sales_invoice.name,
            "sales_invoice_date": sales_invoice.posting_date
            or (sales_invoice.creation.date() if sales_invoice.creation else "N/A"),
            "ewaybill_no": sales_invoice.ewaybill or "N/A",
            "ewaybill_generation_date": sales_invoice.ewaybill_date.date()
            if hasattr(sales_invoice, "ewaybill_date") and sales_invoice.ewaybill_date
            else "N/A",
        }
    )


def update_row_with_installation_note(row, installation_note):
    row.update(
        {
            "installation_note_id": installation_note.name,
            "installation_note_date": installation_note.creation.date() if installation_note.creation else "N/A",
            "installation_remarks": installation_note.remarks or "N/A",
        }
    )


def update_row_with_discom(row, discom):
    row.update(
        {
            "discom_status": discom.discom_status or "N/A",
            "load_enhancement": discom.custom_load_enhancement or "N/A",
            "load_number": discom.custom_load_number or "N/A",
            "meter_draw_date": discom.meter_drawn_date or "N/A",
            "meter_fitting_date": discom.meter_fitting_date or "N/A",
            "synchronization_date": discom.synchronization_date or "N/A",
            "done_by": "N/A",
        }
    )


def update_row_with_subsidy(row, subsidy):
    row.update(
        {
            "pcr_date": subsidy.pcr_submit_date or "N/A",
            "subsidy_status": subsidy.subsidy_status or "N/A",
            "subsidy_amt_received_date": subsidy.subsidy_cheque_date or "N/A",
            "subsidy_amount": subsidy.custom_subsidy_amount or 0,
        }
    )
