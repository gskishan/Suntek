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
		this.$wrapper = $(wrapper);
		this.bodyTextColor = getComputedStyle(document.body).getPropertyValue("--text-color");
		this.setup(wrapper);
		frappe.run_serially([() => this.get_data(), () => this.render()]);
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
		this.lead_owner_field = wrapper.page.add_field({
			fieldtype: "Link",
			fieldname: "lead_owner",
			options: "User",
			label: __("Lead Owner"),
			change: function () {
				me.lead_owner = this.value;
				me.get_data();
			},
		});
		this.source_field = wrapper.page.add_field({
			fieldtype: "Link",
			fieldname: "source",
			options: "Lead Source",
			label: __("Source"),
			change: function () {
				me.source = this.value;
				me.get_data();
			},
		});

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
				lead_owner: this.lead_owner || "",
				source: this.source || "",
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

		if (!this.options.data || !this.options.data.length) {
			this.elements.no_data.toggle(true);
			return;
		}

		this.elements.canvas.on("mousemove", function (e) {
			const boundingBox = this.getBoundingClientRect();
			const scaleX = this.width / boundingBox.width;
			const scaleY = this.height / boundingBox.height;
			const mouseX = (e.clientX - boundingBox.left) * scaleX;
			const mouseY = (e.clientY - boundingBox.top) * scaleY;

			let currentY = 20;
			let hoveredSection = null;

			me.options.data.forEach((d, i) => {
				const height = d.height;
				const y_start = currentY;
				const y_end = currentY + height;

				if (mouseY >= y_start && mouseY <= y_end) {
					const current_y_ratio = (y_start - 20) / (me.options.height - 20);
					const section_width = me.options.width * 0.4 * (1 - current_y_ratio);
					const x_start = me.options.width * 0.05 + (me.options.width * 0.4 - section_width) / 2;
					const x_end = x_start + section_width;

					if (mouseX >= x_start && mouseX <= x_end) {
						hoveredSection = i;
					}
				}
				currentY += height;
			});

			me.redrawFunnel(hoveredSection);
		});

		this.elements.canvas.on("mouseout", function () {
			me.redrawFunnel(null);
		});

		this.redrawFunnel();
	}

	redrawFunnel(hoveredIndex = null) {
		const context = this.elements.context;
		const max_width = this.options.width * 0.4;
		let y = 20;

		context.clearRect(0, 0, this.options.width, this.options.height);

		if (!this.options.data || !this.options.data.length) {
			this.elements.no_data.toggle(true);
			return;
		}

		const funnel_offset = this.options.width * 0.05;
		const triangle_base = max_width;
		const triangle_height = this.options.height - y;

		this.options.data.forEach((d, i) => {
			const current_y_ratio = (y - 20) / triangle_height;
			const next_y_ratio = (y + d.height - 20) / triangle_height;
			const current_width = triangle_base * (1 - current_y_ratio);
			const next_width = triangle_base * (1 - next_y_ratio);
			const x_start = funnel_offset + (max_width - current_width) / 2;
			const x_end = x_start + current_width;
			const next_x_start = funnel_offset + (max_width - next_width) / 2;
			const next_x_end = next_x_start + next_width;

			context.fillStyle = d.color;

			if (i === hoveredIndex) {
				context.save();
				context.shadowColor = "rgba(0, 0, 0, 0.5)";
				context.shadowBlur = 15;
				context.fillStyle = this.adjustColor(d.color, 20);
			}

			context.beginPath();
			context.moveTo(x_start, y);
			context.lineTo(x_end, y);

			if (i === this.options.data.length - 1) {
				const finalX = funnel_offset + max_width / 2;
				context.lineTo(finalX, y + d.height);
			} else {
				context.lineTo(next_x_end, y + d.height);
				context.lineTo(next_x_start, y + d.height);
			}

			context.closePath();
			context.fill();

			if (i === hoveredIndex) {
				context.restore();
			}

			const x_mid = (x_start + x_end) / 2;
			this.draw_legend(
				x_mid,
				y + d.height / 2,
				this.options.width,
				this.options.height,
				d.value + " - " + d.title,
				i === hoveredIndex
			);

			y += d.height;
		});
	}

	prepare_funnel() {
		var me = this;
		this.elements.no_data.toggle(false);
		this.options.width = (($(this.elements.funnel_wrapper).width() * 2.0) / 3.0) * 1.5;
		this.options.height = ((Math.sqrt(3) * this.options.width * 0.4) / 2.0) * 1.5;

		const total_value = this.options.data.reduce((sum, d) => sum + d.value, 0);
		const total_height = this.options.height - 20;

		$.each(this.options.data, function (i, d) {
			d.height = (total_height * d.value) / total_value;
		});

		this.elements.funnel_wrapper.empty();
		this.elements.canvas = $("<canvas></canvas>")
			.appendTo(this.elements.funnel_wrapper)
			.attr("width", $(this.elements.funnel_wrapper).width())
			.attr("height", this.options.height);

		this.elements.context = this.elements.canvas.get(0).getContext("2d");
	}

	adjustColor(color, percent) {
		const num = parseInt(color.replace("#", ""), 16),
			amt = Math.round(2.55 * percent),
			R = (num >> 16) + amt,
			G = ((num >> 8) & 0x00ff) + amt,
			B = (num & 0x0000ff) + amt;
		return (
			"#" +
			(
				0x1000000 +
				(R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
				(G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
				(B < 255 ? (B < 1 ? 0 : B) : 255)
			)
				.toString(16)
				.slice(1)
		);
	}

	calculateNextSection(currentWidth, currentY, height) {
		const ratio = (height - currentY) / height;
		return currentWidth * ratio;
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
		context.stroke();
	}
	draw_legend(x_mid, y_mid, width, height, title, isHovered) {
		var context = this.elements.context;
		if (y_mid == 0) y_mid = 7;

		const funnel_width = width * 0.4;
		const line_start = x_mid;
		const line_end = funnel_width + (width - funnel_width) * 0.6;

		context.strokeStyle = context.fillStyle;

		context.beginPath();
		context.moveTo(line_start, y_mid);
		context.lineTo(line_end, y_mid);
		context.closePath();
		context.stroke();
		context.beginPath();
		context.arc(line_end, y_mid, isHovered ? 7 : 5, 0, Math.PI * 2, false);
		context.closePath();
		context.fill();

		context.fillStyle = getComputedStyle(document.body).getPropertyValue("--text-color");
		context.textBaseline = "middle";
		context.font = isHovered ? "bold 1.1em sans-serif" : "1em sans-serif";
		context.fillText(__(title), line_end + 15, y_mid);

		// if (isHovered) {
		// 	const tooltipData = this.getToolTipData(title);
		// 	this.drawtooltip(x_mid, y_mid, tooltipData);
		// }
	}
};

function isPointInTrapezoid(x, y, points) {
	let inside = false;
	for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
		const xi = points[i].x,
			yi = points[i].y;
		const xj = points[j].x,
			yj = points[j].y;

		const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
		if (intersect) inside = !inside;
	}
	return inside;
}
