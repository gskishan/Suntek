import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class ChannelPartnerPurchaseOrder(Document):
    def autoname(self):
        fiscal_year = frappe.defaults.get_user_default("fiscal_year") or ""
        if fiscal_year:
            year = fiscal_year.split("-")[0]
        else:
            year = datetime.date.today().strftime("%Y")

        month = datetime.date.today().strftime("%m")

        self.name = make_autoname(f"CPPO-{year}-{month}-.#####")

    def validate(self):
        self.validate_channel_partner()
        self.validate_type_of_case()
        self.fetch_type_of_case_from_project()
        self.calculate_totals()
        self.update_status()

    def validate_type_of_case(self):
        """Validate that CPPO is not being created for subsidy cases"""
        if self.type_of_case == "Subsidy":
            frappe.throw(
                _("Channel Partner Purchase Orders are not needed for Subsidy cases.")
            )

    def update_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            if self.sales_order:
                self.status = "SO Created"
            else:
                self.status = "Submitted"
        elif self.docstatus == 2:
            self.status = "Cancelled"

    def validate_channel_partner(self):
        """Validate that the channel partner exists and is active"""
        if not frappe.db.exists("Channel Partner", self.channel_partner):
            frappe.throw(
                _("Channel Partner {0} does not exist").format(self.channel_partner)
            )

        channel_partner = frappe.get_doc("Channel Partner", self.channel_partner)
        if channel_partner.status != "Active":
            frappe.throw(
                _("Channel Partner {0} is not active").format(self.channel_partner)
            )

    def fetch_type_of_case_from_project(self):
        """Fetch type_of_case from project if project is specified and type_of_case is not set"""
        if self.project and not self.type_of_case:
            type_of_case = frappe.db.get_value(
                "Project", self.project, "custom_type_of_case"
            )
            if type_of_case:
                self.type_of_case = type_of_case

    def calculate_totals(self):
        """Calculate total quantity, amount, taxes and grand total"""
        self.total = 0
        self.total_qty = 0

        for item in self.items:
            item.amount = item.rate * item.qty
            self.total += item.amount
            self.total_qty += item.qty

        self.total_taxes_and_charges = 0

        if self.taxes_and_charges_template:
            if not self.taxes:
                tax_template = frappe.get_doc(
                    "Sales Taxes and Charges Template", self.taxes_and_charges_template
                )
                for tax in tax_template.taxes:
                    self.append(
                        "taxes",
                        {
                            "charge_type": tax.charge_type,
                            "account_head": tax.account_head,
                            "description": tax.description,
                            "rate": tax.rate,
                        },
                    )

            for tax in self.taxes:
                if tax.charge_type == "Actual":
                    tax_amount = tax.rate
                else:
                    tax_amount = (tax.rate * self.total) / 100

                tax.tax_amount = tax_amount
                self.total_taxes_and_charges += tax_amount

        self.grand_total = self.total + self.total_taxes_and_charges

        if hasattr(self, "advance_amount") and self.advance_amount:
            self.balance_amount = self.grand_total - self.advance_amount
        else:
            self.balance_amount = self.grand_total

    def on_cancel(self):
        """Prevent cancellation if linked sales order exists and is not cancelled"""
        if self.sales_order:
            so_status = frappe.db.get_value("Sales Order", self.sales_order, "status")
            if so_status not in ["Cancelled", "Closed"]:
                frappe.throw(
                    _(
                        "Cannot cancel this order. Please cancel the linked Sales Order {0} first."
                    ).format(self.sales_order)
                )

    @frappe.whitelist()
    def create_sales_order(self):
        try:
            if self.type_of_case == "Subsidy":
                frappe.throw(_("This functionality is not for Subsidy type of cases."))

            if self.sales_order:
                frappe.throw(
                    _(
                        "Sales Order already exists for this Channel Partner Purchase Order."
                    )
                )

            channel_partner = frappe.get_doc("Channel Partner", self.channel_partner)

            if (
                not hasattr(channel_partner, "linked_customer")
                or not channel_partner.linked_customer
            ):
                if hasattr(channel_partner, "create_customer"):
                    customer_name = channel_partner.create_customer()
                    if not customer_name:
                        frappe.throw(
                            _("Could not create customer for Channel Partner.")
                        )
                else:
                    frappe.throw(
                        _(
                            "No customer linked to this Channel Partner and cannot create one."
                        )
                    )
            else:
                customer_name = channel_partner.linked_customer

            if not frappe.db.exists("Customer", customer_name):
                frappe.throw(
                    _(
                        "The customer '{0}' linked to channel partner does not exist."
                    ).format(customer_name)
                )

            sales_order = frappe.new_doc("Sales Order")
            sales_order.flags.ignore_validate = True

            default_price_list = frappe.db.get_value(
                "Selling Settings", None, "selling_price_list"
            )
            company_currency = frappe.db.get_value(
                "Company",
                frappe.defaults.get_user_default("Company"),
                "default_currency",
            )

            sales_order.update(
                {
                    "customer": channel_partner.linked_customer,
                    "transaction_date": frappe.utils.today(),
                    "delivery_date": self.required_by_date,
                    "company": frappe.defaults.get_user_default("Company"),
                    "order_type": "Channel Partner",
                    "channel_partner_purchase_order": self.name,
                    "custom_channel_partner": self.channel_partner,
                    "currency": company_currency,
                    "conversion_rate": 1.0,
                    "price_list_currency": company_currency,
                    "plc_conversion_rate": 1.0,
                    "selling_price_list": default_price_list or "Standard Selling",
                    "custom_suntek_state": channel_partner.state,
                    "custom_suntek_city": channel_partner.city,
                    "custom_suntek_district": channel_partner.district,
                }
            )

            for item in self.items:
                sales_order.append(
                    "items",
                    {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "description": item.description,
                        "qty": item.qty,
                        "uom": item.uom,
                        "rate": item.rate,
                        "conversion_factor": 1.0,
                        "delivery_date": self.required_by_date,
                    },
                )

            if self.taxes_and_charges_template:
                sales_order.taxes_and_charges = self.taxes_and_charges_template
                for tax in self.taxes:
                    sales_order.append(
                        "taxes",
                        {
                            "charge_type": tax.charge_type,
                            "account_head": tax.account_head,
                            "description": tax.description,
                            "rate": tax.rate,
                        },
                    )

            sales_order.flags.ignore_permissions = True

            try:
                sales_order.insert()
            except Exception as insertion_error:
                frappe.log_error(
                    f"Sales Order creation failed: {str(insertion_error)}\n"
                    f"Customer: {customer_name}\n"
                    f"Project: {self.project}\n"
                    f"Document data: {sales_order.as_dict()}",
                    "Sales Order Creation Detailed Error",
                )
                raise

            self.db_set("sales_order", sales_order.name)
            self.db_set("status", "SO Created")

            frappe.msgprint(
                _("Sales Order {0} created successfully").format(sales_order.name)
            )
            return sales_order.name

        except Exception as e:
            frappe.log_error(str(e), "Sales Order Creation Error")
            frappe.throw(str(e))

    @frappe.whitelist()
    def fetch_details_from_project_sales_order(self, project):
        if not project:
            frappe.msgprint(_("No project specified"))
            return None

        if not frappe.db.exists("Project", project):
            frappe.msgprint(_("Project {0} not found").format(project))
            return None

        frappe.msgprint(f"Looking for sales orders for project: {project}")

        sales_orders = frappe.db.sql(
            """
            SELECT name, docstatus, transaction_date, terms
            FROM `tabSales Order` 
            WHERE project = %s
            ORDER BY transaction_date DESC, modified DESC
        """,
            project,
            as_dict=1,
        )

        if not sales_orders:
            project_customer = frappe.db.get_value("Project", project, "customer")
            if project_customer:
                frappe.msgprint(
                    f"No direct project link found. Trying to find sales orders with customer: {project_customer}"
                )
                sales_orders = frappe.db.sql(
                    """
                    SELECT name, docstatus, transaction_date, terms
                    FROM `tabSales Order` 
                    WHERE customer = %s
                    ORDER BY transaction_date DESC, modified DESC
                    LIMIT 5
                """,
                    project_customer,
                    as_dict=1,
                )

        if not sales_orders:
            frappe.msgprint(
                _(
                    "No Sales Orders found for this project. Please create a Sales Order first."
                )
            )
            return None

        orders_list = "\n".join(
            [
                f"- {so.name} (Status: {'Submitted' if so.docstatus == 1 else 'Draft'})"
                for so in sales_orders
            ]
        )
        frappe.msgprint(f"Found sales orders:\n{orders_list}")

        submitted_so = None
        for so in sales_orders:
            if so.docstatus == 1:
                submitted_so = so
                break

        if not submitted_so and sales_orders:
            submitted_so = sales_orders[0]
            frappe.msgprint(_("Using draft sales order: {0}").format(submitted_so.name))
        elif not submitted_so:
            frappe.msgprint(_("No Sales Orders found."))
            return None
        else:
            frappe.msgprint(
                _("Using submitted sales order: {0}").format(submitted_so.name)
            )

        items = frappe.get_all(
            "Sales Order Item",
            filters={"parent": submitted_so.name},
            fields=[
                "item_code",
                "item_name",
                "description",
                "qty",
                "uom",
                "rate",
                "amount",
                "warehouse",
            ],
        )

        if not items:
            frappe.msgprint(
                _("No items found in sales order {0}").format(submitted_so.name)
            )

        taxes = []
        try:
            taxes = frappe.get_all(
                "Sales Taxes and Charges",
                filters={"parent": submitted_so.name},
                fields=[
                    "charge_type",
                    "account_head",
                    "description",
                    "rate",
                    "tax_amount",
                ],
            )

            if taxes:
                frappe.msgprint(f"Found {len(taxes)} tax entries")
            else:
                frappe.msgprint("No tax entries found")
        except Exception as e:
            frappe.msgprint(f"Error fetching taxes: {str(e)}")

        tax_template = None
        try:
            if frappe.db.has_column("Sales Order", "taxes_and_charges"):
                tax_template = frappe.db.get_value(
                    "Sales Order", submitted_so.name, "taxes_and_charges"
                )
        except Exception:
            pass

        result = {
            "sales_order": submitted_so.name,
            "items": items,
            # "taxes": taxes,
        }

        if tax_template:
            result["taxes_and_charges_template"] = tax_template

        if hasattr(submitted_so, "terms") and submitted_so.terms:
            result["terms"] = submitted_so.terms

        try:
            if frappe.db.has_column("Sales Order", "terms_and_conditions"):
                tc = frappe.db.get_value(
                    "Sales Order", submitted_so.name, "terms_and_conditions"
                )
                if tc:
                    result["terms_and_conditions"] = tc
        except Exception:
            pass
        return result

    @frappe.whitelist()
    def fetch_details_from_quotation(self, quotation):
        if not quotation:
            frappe.msgprint(_("No quotation specified"))
            return None
        if not frappe.db.exists("Quotation", quotation):
            frappe.msgprint(_("Quotation does not exist"))
            return None

        try:
            quotation_doc = frappe.get_doc("Quotation", quotation)

            if quotation_doc.status in ["Draft", "Cancelled"]:
                frappe.msgprint(
                    _("Cannot use draft / cancelled quotation"),
                    title="Draft / Cancelled Quotation",
                    indicator="red",
                )
                return None

            items = []
            for item in quotation_doc.items:
                items.append(
                    {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "description": item.description,
                        "qty": item.qty,
                        "uom": item.uom,
                        "rate": item.rate,
                        "amount": item.amount,
                        "warehouse": item.warehouse
                        if hasattr(item, "warehouse")
                        else None,
                    }
                )

            if not items:
                frappe.msgprint(_(f"Items not found in Quotation: {quotation}"))
            #
            # taxes = []
            # if hasattr(quotation_doc, "taxes"):
            #     for tax in quotation_doc.taxes:
            #         taxes.append(
            #             {
            #                 "charge_type": tax.charge_type,
            #                 "account_head": tax.account_head,
            #                 "description": tax.description,
            #                 "rate": tax.rate,
            #                 "tax_amount": tax.tax_amount
            #                 if hasattr(tax, "tax_amount")
            #                 else None,
            #             }
            #         )
            #
            #         result = {"quotation": quotation, "items": items, "taxes": taxes}

            result = {
                "quotation": quotation,
                "items": items,
            }

            self.type_of_case = quotation_doc = quotation_doc.custom_type_of_case
            return result

        except Exception as e:
            frappe.log_error(
                title="Channel Partner Purchase Order Error",
                message=str(e),
                reference_doctype="Channel Partner Purchase Order",
                reference_name=self.name,
            )
            frappe.msgprint(_(f"Error fetching quotation details: {str(e)}"))
            return None
