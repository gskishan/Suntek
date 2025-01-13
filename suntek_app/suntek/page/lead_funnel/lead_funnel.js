frappe.pages["lead-funnel"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Lead Funnel"),
		single_column: true,
	});

	wrapper.lead_funnel = new erpnext.LeadFunnel(wrapper);
	frappe.breadcrumbs.add("Suntek");
};

erpnext.LeadFunnel = class LeadFunnel {
	constructor(wrapper) {
		var me = this;
		me.setup(wrapper);
		frappe.run_serially([() => me.get_data(), () => me.render()]);
	}

	setup(wrapper) {
		var me = this;

		this.company_field = wrapper.page.add_field({
			fieldtype: "Link",
			fieldname: "company",
			options: "Company",
			label: __("Company"),
			reqd: 1,
			default: frappe.defaults.get_user_default("company"),
			change: function () {
				me.company = this.value || frappe.defaults.get_user_default("company");
				me.get_data();
			},
		});

		this.elements = {
			layout: $(wrapper).find(".layout-main"),
			from_date: wrapper.page.add_date(__("From Date")),
			to_date: wrapper.page.add_date(__("To Date")),
			refresh_btn: wrapper.page.set_primary_action(__("Refresh"), function () {
				me.get_data();
			}),
		};

		this.elements.no_data = $(
			'<div class="alert alert-warning" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">' +
				__("No Data Available") +
				"</div>"
		)
			.toggle(false)
			.appendTo(this.elements.layout);

		this.elements.funnel_wrapper = $(
			'<div class="funnel-wrapper text-center" style="width: 100%; padding: 20px;"></div>'
		).appendTo(this.elements.layout);

		this.company = frappe.defaults.get_user_default("company");
		this.options = {
			from_date: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			to_date: frappe.datetime.get_today(),
		};

		// set defaults and bind on change
		$.each(["from_date", "to_date"], function (i, field) {
			me.elements[field].val(frappe.datetime.str_to_user(me.options[field]));
			me.elements[field].on("change", function () {
				me.options[field] =
					frappe.datetime.user_to_str($(this).val()) || frappe.datetime.get_today();
				me.get_data();
			});
		});

		$(window).resize(function () {
			me.render();
		});
	}

	get_data(btn) {
		var me = this;
		if (!this.company) {
			this.company = frappe.defaults.get_user_default("company");
		}

		return frappe.call({
			method: "suntek_app.suntek.page.lead_funnel.lead_funnel.get_funnel_data",
			args: {
				from_date: this.options.from_date,
				to_date: this.options.to_date,
				company: this.company,
			},
			btn: btn,
			callback: function (r) {
				if (!r.exc) {
					me.options.data = r.message;
					me.render();
				}
			},
		});
	}

	render() {
		this.render_funnel();
	}

	render_funnel() {
		var me = this;
		this.prepare_funnel();
		this.elements.context.clearRect(0, 0, this.options.width, this.options.height);

		var context = this.elements.context,
			max_width = this.options.width * 0.8,
			y = 20;

		if (!this.options.data || !this.options.data.length) {
			this.elements.no_data.toggle(true);
			return;
		}

		this.options.data.forEach((d, i) => {
			const section_width = max_width * d.width_factor;
			const x_start = (this.options.width - section_width) / 2;
			const x_end = x_start + section_width;
			const x_mid = (x_start + x_end) / 2;

			context.beginPath();
			context.fillStyle = d.color;
			context.strokeStyle = d.color;

			if (i === 0) {
				context.moveTo(x_start, y);
				context.lineTo(x_end, y);
			} else {
				const prev_width = max_width * this.options.data[i - 1].width_factor;
				const prev_x_start = (this.options.width - prev_width) / 2;
				const prev_x_end = prev_x_start + prev_width;
				context.moveTo(prev_x_start, y);
				context.lineTo(prev_x_end, y);
			}

			// Draw bottom of section
			const next_y = y + d.height;
			context.lineTo(x_end, next_y);
			context.lineTo(x_start, next_y);
			context.closePath();
			context.fill();

			// Draw legend
			this.draw_legend(
				x_mid,
				y + d.height / 2,
				this.options.width,
				this.options.height,
				d.value + " - " + d.title
			);

			y = next_y;
		});
	}

	prepare_funnel() {
		var me = this;
		this.elements.no_data.toggle(false);

		const container_width = $(this.elements.funnel_wrapper).width();
		const window_height = $(window).height();

		this.options.width = Math.min(container_width * 0.8, 1200);
		this.options.height = Math.min(window_height * 0.75, 900);
		this.options.data = this.options.data.sort((a, b) => b.value - a.value);

		const min_height = (this.options.height * 0.1) / (this.options.data?.length || 1);
		const height = this.options.height * 0.9;
		const max_value = Math.max(...this.options.data.map((d) => d.value));
		// const total_value = this.options.data.reduce((sum, d) => sum + d.value, 0);

		$.each(this.options.data, function (i, d) {
			d.height = height / me.options.data.length + min_height;
			d.width_factor = Math.sqrt(d.value / max_value);
		});

		this.elements.funnel_wrapper.empty();

		const container = $(
			'<div style="display: flex; justify-content: flex-start; width: 100%; padding-left: 10%;"></div>'
		).appendTo(this.elements.funnel_wrapper);

		// Create new canvas
		this.elements.canvas = $("<canvas></canvas>")
			.appendTo(container)
			.attr("width", this.options.width)
			.attr("height", this.options.height)
			.css({
				"max-width": "100%",
				height: "auto",
			});

		this.elements.context = this.elements.canvas.get(0).getContext("2d");
		this.elements.context.lineWidth = 2;
		this.elements.context.strokeStyle = "#fff";
	}

	draw_triangle(x_start, x_mid, x_end, y, height) {
		var context = this.elements.context;
		context.beginPath();
		context.moveTo(x_start, y);
		context.lineTo(x_end, y);
		context.lineTo(x_mid, height);
		context.lineTo(x_start, y);
		context.closePath();
		context.fill();
	}

	draw_legend(x_mid, y_mid, width, height, title) {
		var context = this.elements.context;
		if (y_mid == 0) y_mid = 7;

		const line_start = x_mid;
		const line_end = width * 0.75;

		context.beginPath();
		context.moveTo(line_start, y_mid);
		context.lineTo(line_end, y_mid);
		context.closePath();
		context.stroke();

		context.beginPath();
		context.arc(line_end, y_mid, 5, 0, Math.PI * 2, false);
		context.closePath();
		context.fill();

		context.fillStyle = getComputedStyle(document.body).getPropertyValue("--text-color");
		context.textBaseline = "middle";
		context.font = "1.1em sans-serif";
		context.fillText(__(title), line_end + 15, y_mid);
	}
};
