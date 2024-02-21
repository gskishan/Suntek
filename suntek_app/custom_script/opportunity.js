frappe.ui.form.on('Opportunity', {
  opportunity_owner: function (frm) {
        if (frm.opportunity_owner) {
            frappe.call({
                method: "suntek_app.custom_script.opportunity.get_emp",
                args: {
                    "user": frm.opportunity_owner,

                }, callback: function (r) {
                    console.log(r)
                   

                }
            })
        }


    }



})
