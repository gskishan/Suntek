frappe.ui.form.on("State Head", {
    state_head_user_id: function (frm) {
        frm.call({
            method: "fetch_employee_id_from_user",
            doc: frm.doc,
            callback: function (r) {
                if (r.message) {
                    frm.set_value("state_head_employee_id", r.message.employee_id);
                }
            },
        });
    },
});
