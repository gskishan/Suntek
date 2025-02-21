frappe.ui.form.on("Channel Partner", {
  refresh: function (frm) {
    frm.dashboard_data = {};
    refresh_dashboard(frm);
  },
  onload: function (frm) {
    $(document).on("click", `[data-fieldname="dashboard_tab"]`, function () {
      refresh_dashboard(frm);
    });
  },
});

function refresh_dashboard(frm) {
  frappe.call({
    method:
      "suntek_app.channel_partner.doctype.channel_partner.channel_partner_dashboard.get_dashboard_data",
    args: {
      channel_partner: frm.doc.name,
    },
    callback: function (r) {
      if (!r.exc) {
        frm.dashboard_data = r.message;
        render_dashboard(frm);
      }
    },
  });
}

function render_dashboard(frm) {
  const data = frm.dashboard_data;

  const dashboard_html = `
        <div class="dashboard-section">
            <!-- Stats Cards Section -->
            <div class="row dashboard-stats">
                <!-- Sales Orders Card -->
                <div class="col-md-4">
                    <div class="card clickable-card" onclick="window.location.href='/app/sales-order?custom_channel_partner=${encodeURIComponent(frm.doc.name)}&status=To%20Deliver%20and%20Bill,To%20Bill,To%20Deliver'">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">Open Sales Orders</h6>
                            <h2 class="card-title">${data.open_sales_orders || 0}</h2>
                            <div class="progress">
                                <div class="progress-bar bg-success" style="width: ${(data.open_sales_orders / data.total_sales_orders) * 100 || 0}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Opportunities Card -->
                <div class="col-md-4">
                    <div class="card clickable-card" onclick="window.location.href='/app/opportunity?custom_channel_partner=${encodeURIComponent(frm.doc.name)}&status=Open'">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">Open Opportunities</h6>
                            <h2 class="card-title">${data.open_opportunities || 0}</h2>
                            <div class="progress">
                                <div class="progress-bar bg-primary" style="width: ${(data.open_opportunities / data.total_opportunities) * 100 || 0}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Leads Card -->
                <div class="col-md-4">
                    <div class="card clickable-card" onclick="window.location.href='/app/lead?custom_channel_partner=${encodeURIComponent(frm.doc.name)}&status=Open'">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">Open Leads</h6>
                            <h2 class="card-title">${data.open_leads || 0}</h2>
                            <div class="progress">
                                <div class="progress-bar bg-warning" style="width: ${(data.open_leads / data.total_leads) * 100 || 0}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Orders Table -->
            ${
              data.recent_orders && data.recent_orders.length
                ? `
            <div class="recent-orders mt-4">
                <h5>Recent Sales Orders</h5>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr class="table-head">
                                <th scope="col">Order ID</th>
                                <th scope="col">Date</th>
                                <th scope="col">Amount</th>
                                <th scope="col">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.recent_orders
                              .map(
                                (order) => `
                                <tr>
                                    <td>
                                        <a href="/app/sales-order/${order.name}">${order.name}</a>
                                    </td>
                                    <td>${frappe.datetime.str_to_user(order.transaction_date)}</td>
                                    <td>${format_currency(order.grand_total)}</td>
                                    <td><span class="indicator-pill ${get_status_color(order.status)}">${order.status}</span></td>
                                </tr>
                            `,
                              )
                              .join("")}
                        </tbody>
                    </table>
                </div>
            </div>
            `
                : ""
            }
        </div>
    `;

  $(frm.fields_dict.dashboard_html.wrapper).html(dashboard_html);
}

function get_status_color(status) {
  const status_colors = {
    Draft: "gray",
    "On Hold": "orange",
    "To Deliver and Bill": "blue",
    "To Bill": "orange",
    "To Deliver": "yellow",
    Completed: "green",
    Cancelled: "red",
    Closed: "gray",
  };
  return status_colors[status] || "gray";
}

frappe.dom.set_style(`
    .dashboard-section {
        padding: 15px;
    }
    .dashboard-stats .card {
        box-shadow: 0 2px 4px var(--shadow-sm);
        margin-bottom: 15px;
        border-radius: 8px;
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
    }
    .dashboard-stats .card-body {
        padding: 15px;
    }
    .dashboard-stats .card-title {
        margin-bottom: 15px;
        color: var(--text-color);
    }
    .dashboard-stats .card-subtitle {
        color: var(--text-muted);
    }
    .dashboard-stats .progress {
        height: 4px;
        margin-top: 10px;
        background-color: var(--gray-200);
    }
    .recent-orders {
        background: var(--card-bg);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    .recent-orders h5 {
        color: var(--text-color);
    }
    .  .table {
        color: var(--text-color);
        background-color: var(--card-bg);
    }
    .table-head {
        background-color: var(--fg-color);
    }
    .table thead th {
        border-bottom: 1px solid var(--border-color);
        background-color: var(--fg-color);
        color: var(--text-color);
        font-weight: 600;
    }
    .table td {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
    }
    .table tbody tr:hover td {
        background-color: var(--fg-hover-color);
    }dashboard-stats .card:hover {
        transform: translateY(-2px);
        transition: transform 0.2s ease;
    }
    .dashboard-stats a {
        color: var(--text-color);
        text-decoration: none;
    }
    .dashboard-stats a:hover {
        color: var(--primary);
    }
    .clickable-card {
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .clickable-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px var(--shadow-sm);
    }

    .clickable-card:active {
        transform: translateY(0);
    }
    .clickable-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--text-color);
        opacity: 0;
        transition: opacity 0.2s;
        border-radius: 8px;
    }

    .clickable-card:hover::after {
        opacity: 0.02;
    }
`);
