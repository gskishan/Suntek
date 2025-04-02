frappe.ui.form.on("Item", {
  onload: function (frm) {
    setTimeout(() => {
      frappe.model.with_doctype("Channel Partner", function () {
        if (frappe.perm.has_perm("Channel Partner", 0, "read")) {
          frappe.call({
            method: "frappe.client.get_list",
            args: {
              doctype: "Channel Partner",
              filters: {
                linked_user: frappe.session.user,
              },
              fields: ["name"],
              limit_page_length: 1,
            },
            callback: function (r) {
              if (r.message && r.message.length > 0) {
                setTimeout(() => {
                  try {
                    const tabNameMap = {
                      dashboard_tab: ["dashboard"],
                      inventory_section: ["inventory"],
                      variants_section: ["variants", "variant"],
                      accounting: ["accounting"],
                      purchasing_tab: ["purchasing"],
                      sales_details: ["sales", "sale details"],
                      item_tax_section_break: ["item tax", "tax"],
                      quality_tab: ["quality"],
                      manufacturing: ["manufacturing"],
                    };

                    if ($(".form-tabs .nav-item .nav-link").length) {
                      $(".form-tabs .nav-item .nav-link").each(function () {
                        const $tab = $(this);
                        const tabText = $tab.text().trim().toLowerCase();
                        const dataTab = $tab.attr("data-tab");

                        let shouldHide = false;

                        for (const [
                          exactName,
                          displayOptions,
                        ] of Object.entries(tabNameMap)) {
                          if (
                            displayOptions.some((opt) =>
                              tabText.includes(opt.toLowerCase())
                            ) ||
                            (dataTab &&
                              (dataTab === exactName ||
                                dataTab.includes(exactName)))
                          ) {
                            shouldHide = true;
                            break;
                          }
                        }

                        if (shouldHide) {
                          $tab.parent(".nav-item").hide();
                        }
                      });

                      $('.form-tabs .nav-link:contains("Sale")')
                        .parent(".nav-item")
                        .hide();
                      $('.form-tabs .nav-link:contains("Tax")')
                        .parent(".nav-item")
                        .hide();

                      $(".form-tabs .nav-link")
                        .filter(function () {
                          const text = $(this).text().toLowerCase();
                          return (
                            text.includes("sale") ||
                            text.includes("sales") ||
                            text.includes("tax") ||
                            text.includes("item tax")
                          );
                        })
                        .parent(".nav-item")
                        .hide();

                      $('.form-tabs .nav-link:contains("Dashboard")')
                        .parent(".nav-item")
                        .hide();
                    }

                    if (frm.dashboard && frm.dashboard.wrapper) {
                      $(frm.dashboard.wrapper).hide();
                    }
                  } catch (e) {
                    console.error("Error in Item form customization:", e);
                  }
                }, 1);
              }
            },
          });
        }
      });
    }, 1);
  },
});
