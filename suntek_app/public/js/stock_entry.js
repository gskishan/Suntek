frappe.ui.form.on("Stock Entry", {
    refresh: function (frm, doc, dt, dn) {
        frm.add_custom_button(__('Designing'),
            function () {
                if (!cur_frm.doc.project) {
                    frappe.throw({
                        title: __("Mandatory"),
                        message: __("Please Select a Project")
                    });
                }
                else {
                    erpnext.utils.map_current_doc({
                        method: "suntek_app.suntek.doctype.designing.designing.make_stock_entry",
                        source_doctype: "Designing",
                        target: frm,
                        setters: {
                            custom_project: frm.doc.project,
                        },
                        get_query_filters: {
                            custom_project: frm.doc.project,
                            docstatus: 1,
                        },

                    })
                }

            }, __("Get Items From"));

    },
    setup: function (frm) {
        cur_frm.cscript.onload = function () {
            frm.set_query("work_order", function () {
                return {
                    filters: [
                        ["Work Order", "docstatus", "=", 1],
                        ["Work Order", "qty", ">", "`tabWork Order`.produced_qty"],
                        ["Work Order", "company", "=", frm.doc.company],
                        ["Work Order", "project", "=", frm.doc.project],
                    ],
                };
            });



        }
    },
        // stock_entry_type: function (frm) {
        //     if (frm.doc.stock_entry_type == "Material Transfer to Customer" && frm.doc.project) {
        //         frappe.db.get_value('Project', cur_frm.doc.project, 'customer',)
        //             .then(r => {
        //                 if (r.message["customer"] !== null) {
        //                     frm.set_value("customer", r.message["customer"]);
        //                 }

        //             })


        //     }
        // }


    customer: function (frm) {
        if (frm.doc.customer) {
            frappe.call({
                method:"suntek_app.suntek.custom.stock_entry.get_address_display",
                args: {
                    party: frm.doc.customer
                },
                callback: function(response) {
                    var address = response.message
                    console.log(address)
                    if (!response.exc) {

                        frm.set_value("customer_address", address.customer_address);
                        frm.set_value("custom_address_display", address.address_display);
                        frm.set_value("custom_shipping_address_name", address.shipping_address_name);
                        frm.set_value("custom_shipping_addresses", address.shipping_address);
            
                    }
                }
            })
        }
        if (frm.doc.customer) {
            frm.fields_dict.customer_address.get_query = function (doc, cdt, cdn) {
                var d = locals[cdt][cdn];
                    console.log(d)
                return {
                    filters: {
                        "link_doctype": "Customer",
                        "link_name": d.customer
                    }
                };
            };
        }

        if (frm.doc.customer) {
            frm.fields_dict.custom_shipping_address_name.get_query = function (doc, cdt, cdn) {
                var d = locals[cdt][cdn];
                return {
                    filters: {
                        "link_doctype": "Customer",
                        "link_name": d.customer
                    }
                };
            };
        }
        
    
    },
    customer_address:function(frm){
        if (frm.doc.customer_address){
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Address",
                    name: frm.doc.customer_address,
                },
                callback: function(response) {
                    if (response.message){
                        var address = response.message;
                        console.log(address)
                        var custom_address_display = '';
                        if (address.address_line1) custom_address_display += address.address_line1 + '\n';
                        if (address.address_line2) custom_address_display += address.address_line2 + '\n';
                        if (address.city) custom_address_display += address.city + '\n';
                        if (address.state) custom_address_display += address.state + '\n';
                        if (address.pincode) custom_address_display += address.pincode + '\n';
                        if (address.country) custom_address_display += address.country + '\n';
                        if (address.email_id) custom_address_display += address.email_id + '\n';
                        if (address.phone) custom_address_display += address.phone;

                        // Use cur_frm.set_value to update the field
                        frm.set_value('custom_address_display', custom_address_display);
                    }
                    console.log(response)
                }
            })

        }

    },
    custom_shipping_address_name:function(frm){
        if (frm.doc.custom_shipping_address_name){
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Address",
                    name: frm.doc.custom_shipping_address_name,
                },
                callback: function(response) {
                    if (response.message){
                        var address = response.message;
                        console.log(address)
                        var custom_shipping_address = '';
                        if (address.address_line1) custom_shipping_address += address.address_line1 + '\n';
                        if (address.address_line2) custom_shipping_address += address.address_line2 + '\n';
                        if (address.city) custom_shipping_address += address.city + '\n';
                        if (address.state) custom_shipping_address += address.state + '\n';
                        if (address.pincode) custom_shipping_address += address.pincode + '\n';
                        if (address.country) custom_shipping_address += address.country + '\n';
                        if (address.email_id) custom_shipping_address += address.email_id + '\n';
                        if (address.phone) custom_shipping_address += address.phone;

                        // Use cur_frm.set_value to update the field
                        frm.set_value('custom_shipping_addresses', custom_shipping_address);
                    }
                    console.log(response)
                }
            })

        }

    },
    custom_dispatch_address_name:function(frm){
        if (frm.doc.custom_dispatch_address_name){
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Address",
                    name: frm.doc.custom_dispatch_address_name,
                },
                callback: function(response) {
                    if (response.message){
                        var address = response.message;
                        console.log(address)
                        var custom_dispatch_address = '';
                        if (address.address_line1) custom_dispatch_address += address.address_line1 + '\n';
                        if (address.address_line2) custom_dispatch_address += address.address_line2 + '\n';
                        if (address.city) custom_dispatch_address += address.city + '\n';
                        if (address.state) custom_dispatch_address += address.state + '\n';
                        if (address.pincode) custom_dispatch_address += address.pincode + '\n';
                        if (address.country) custom_dispatch_address += address.country + '\n';
                        if (address.email_id) custom_dispatch_address += address.email_id + '\n';
                        if (address.phone) custom_dispatch_address += address.phone;

                        // Use cur_frm.set_value to update the field
                        frm.set_value('custom_dispatch_address', custom_dispatch_address);
                    }
                    console.log(response)
                }
            })

        }

    },
   
    company: function(frm){
        if (frm.doc.company){
            frm.fields_dict.custom_dispatch_address_name.get_query = function (doc, cdt, cdn) {
                var d = locals[cdt][cdn];
                    console.log(d)
                return {
                    filters: {
                        "link_doctype": "Company",
                        "link_name": d.company
                    }
                };
            };
        }
    },
})
