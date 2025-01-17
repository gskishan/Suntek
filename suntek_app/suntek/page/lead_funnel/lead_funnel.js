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

		this.add_filter_buttons(wrapper);

		wrapper.page.add_button(
			__("Clear Filters"),
			function () {
				// Reset all filter buttons
				$(".date-filter-buttons .btn-selected").removeClass("btn-selected");

				// Reset dates to default
				me.options.from_date = frappe.datetime.add_months(frappe.datetime.get_today(), -1);
				me.options.to_date = frappe.datetime.get_today();

				// Update date fields
				me.elements.from_date.val(frappe.datetime.str_to_user(me.options.from_date));
				me.elements.to_date.val(frappe.datetime.str_to_user(me.options.to_date));

				// Clear other filters
				me.lead_owner_field.set_value("");
				me.source_field.set_value("");
				me.lead_owner = "";
				me.source = "";

				// Refresh data
				me.get_data();
			},
			"btn-default btn-sm"
		);

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

	add_filter_buttons(wrapper) {
		const me = this;

		const filter_container = $(`
		<div class="filter-container" style="
			margin: 0 -15px;
			padding: 15px;
			background: var(--fg-color);
			border-bottom: 1px solid var(--border-color);
		">
			<div class="filter-sections" style="
					display: flex;
					flex-wrap: wrap;
					gap: 24px;
					align-items: flex-start;
					position: relative;
			">
					<div class="date-filters" style="
							display: flex;
							flex-direction: column;
							gap: 12px;
					">
							<label style="
									font-size: 0.9em;
									color: var(--text-muted);
									margin-bottom: 0;
									padding-left: 1px;
							">Quick Filters</label>
							<div class="button-group date-filter-buttons" style="
									display: flex;
									gap: 12px;
									flex-wrap: wrap;
							"></div>
					</div>
			</div>
	</div>
`).insertAfter(wrapper.page.page_form);

		// Add date filter buttons
		const date_button_group = filter_container.find(".date-filter-buttons");
		const date_filters = [
			{
				label: "Today",
				icon: "calendar",
				action: () => {
					const today = frappe.datetime.get_today();
					me.set_date_filter(today, today);
				},
			},
			{
				label: "Yesterday",
				icon: "calendar",
				action: () => {
					const yesterday = frappe.datetime.add_days(frappe.datetime.get_today(), -1);
					me.set_date_filter(yesterday, yesterday);
				},
			},
			{
				label: "This Week",
				icon: "calendar",
				action: () => {
					const today = frappe.datetime.get_today();
					const week_start = frappe.datetime.add_days(
						today,
						-frappe.datetime.get_day_diff(today, frappe.datetime.week_start())
					);
					me.set_date_filter(week_start, today);
				},
			},
			{
				label: "Last Week",
				icon: "calendar",
				action: () => {
					const today = frappe.datetime.get_today();
					const week_start = frappe.datetime.add_days(
						today,
						-frappe.datetime.get_day_diff(today, frappe.datetime.week_start()) - 7
					);
					const week_end = frappe.datetime.add_days(week_start, 6);
					me.set_date_filter(week_start, week_end);
				},
			},
			{
				label: "This Month",
				icon: "calendar",
				action: () => {
					const today = frappe.datetime.get_today();
					const month_start = frappe.datetime.month_start();
					me.set_date_filter(month_start, today);
				},
			},
			{
				label: "Last Month",
				icon: "calendar",
				action: () => {
					const today = frappe.datetime.get_today();
					const last_month_start = frappe.datetime.add_months(frappe.datetime.month_start(), -1);
					const last_month_end = frappe.datetime.add_days(frappe.datetime.month_start(), -1);
					me.set_date_filter(last_month_start, last_month_end);
				},
			},
			{
				label: "This Quarter",
				icon: "calendar",
				action: () => {
					const today = frappe.datetime.get_today();
					const quarter_start = frappe.datetime.quarter_start();
					me.set_date_filter(quarter_start, today);
				},
			},
			{
				label: "This FY",
				icon: "calendar",
				action: () => {
					const today = frappe.datetime.get_today();
					const year = frappe.datetime.str_to_obj(today).getFullYear();
					let fiscal_year_start, fiscal_year_end;

					if (frappe.datetime.str_to_obj(today).getMonth() < 3) {
						fiscal_year_start = year - 1 + "-04-01";
						fiscal_year_end = year + "-03-31";
					} else {
						fiscal_year_start = year + "-04-01";
						fiscal_year_end = year + 1 + "-03-31";
					}

					me.set_date_filter(fiscal_year_start, fiscal_year_end);
				},
			},
		];

		// Add buttons for date filters
		date_filters.forEach((filter) => {
			$(`<button class="btn btn-default btn-sm" style="
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 6px 12px;
            border-radius: 6px;
            transition: all 0.2s;
            background: var(--control-bg);
            border: 1px solid var(--border-color);
            min-width: 100px;
            justify-content: center;
        ">
            <i class="fa fa-${filter.icon}"></i>
            ${filter.label}
        </button>`)
				.click(function () {
					date_button_group.find(".btn-selected").removeClass("btn-selected");
					$(this).addClass("btn-selected");
					filter.action();
				})
				.appendTo(date_button_group);
		});

		$("<style>")
			.prop("type", "text/css")
			.html(
				`
			.btn-selected {
				background: var(--primary) !important;
				color: white !important;
				border-color: var(--primary) !important;
			}
			.custom-filter-buttons .btn:hover,
			.date-filter-buttons .btn:hover,
			.clear-filters:hover {
				background: var(--fg-hover-color);
				transform: translateY(-1px);
				box-shadow: var(--shadow-sm);
			}
			.filter-container {
				box-shadow: var(--shadow-sm);
			}
			.filter-sections {
				position: relative;
			}
			.clear-filters {
				position: absolute;
				right: 0;
				top: 0;
			}
		`
			)
			.appendTo("head");
	}

	resetAnimationCache() {
		this._animatedValues = {};
	}
	// Helper method to set date filters
	set_date_filter(from_date, to_date) {
		const me = this;
		me.options.from_date = from_date;
		me.options.to_date = to_date;

		// Update the date fields
		me.elements.from_date.val(frappe.datetime.str_to_user(from_date));
		me.elements.to_date.val(frappe.datetime.str_to_user(to_date));

		// Refresh the data
		me.get_data();
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
					me.options.oldData = me.options.data;
					me.options.data = r.message;
					// Reset animation cache before rendering
					me.resetAnimationCache();
					me.render();
				}
			},
		});
	}

	render() {
		this.render_funnel();
		this.showCalculationDetails();
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

			let hoveredSection = null;
			let y = 20;

			// Check each section for hover
			me.options.data.forEach((d, i) => {
				const max_width = me.options.width * 0.6;
				const min_width = max_width * 0.2;
				const funnel_offset = me.options.width * 0.05;
				const isLastTwoSections = i >= me.options.data.length - 2;

				// Calculate current and next widths
				let current_width, next_width;
				if (isLastTwoSections) {
					current_width = min_width * 1.5;
					next_width = min_width * 1.5;
				} else {
					const progress = i / (me.options.data.length - 2);
					current_width = max_width * (1 - progress * 0.7);
					next_width = max_width * (1 - ((i + 1) / (me.options.data.length - 2)) * 0.7);
				}

				// Calculate coordinates for hit detection
				const x_start = funnel_offset + (max_width - current_width) / 2;
				const x_end = x_start + current_width;
				const next_x_start = funnel_offset + (max_width - next_width) / 2;
				const next_x_end = next_x_start + next_width;
				const current_y = y;
				const next_y = y + d.height;

				// Create trapezoid points
				const points = [
					{ x: x_start, y: current_y },
					{ x: x_end, y: current_y },
					{ x: next_x_end, y: next_y },
					{ x: next_x_start, y: next_y },
				];

				if (isPointInTrapezoid(mouseX, mouseY, points)) {
					hoveredSection = i;
				}

				y += d.height;
			});

			me.redrawFunnel(hoveredSection);
		});

		this.elements.canvas.on("mouseout", function () {
			me.redrawFunnel(null);
		});

		this.redrawFunnel();
	}

	getSimpleDescription(title) {
		if (!this._descriptions) {
			this._descriptions = {
				"Total Leads": "All the leads we received for the given time frame",
				Connected: "Leads that have been contacted",
				Interested: "Leads showing interest in our products",
				Quotation: "Leads that requested pricing",
				Converted: "Leads that became customers",
			};
		}
		return this._descriptions[title] || "";
	}

	animate_number(start, end, duration, callback) {
		const startTime = performance.now();
		const change = end - start;

		const animate = (currentTime) => {
			const elapsed = currentTime - startTime;
			const progress = Math.min(elapsed / duration, 1);

			// Easing function for smooth animation
			const easeOutQuad = (t) => t * (2 - t);
			const currentValue = Math.round(start + change * easeOutQuad(progress));

			callback(currentValue);

			if (progress < 1) {
				requestAnimationFrame(animate);
			}
		};

		requestAnimationFrame(animate);
	}

	showCalculationDetails() {
		$(".calculation-details").remove();

		const calculationHTML = `
        <div class="calculation-details mt-4" style="
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            background: var(--card-bg);
            width: ${this.options.width}px;
            margin: 0 auto;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        ">
            <h6 style="
                color: var(--heading-color);
                font-size: 1.1em;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border-color);
            ">Legend</h6>
            <table class="table calculation-table" style="
                border-collapse: separate;
                border-spacing: 0 0.5rem;
                width: 100%;
                margin-bottom: 0;
            ">
                <tbody>
                    ${this.options.data
											.map(
												(d) => `
                        <tr style="
                            background: var(--fg-color);
                            transition: all 0.2s ease;
                            border-radius: 8px;
                        ">
                            <td style="
                                border: none; 
                                padding: 1rem;
                                color: var(--text-color);
                                width: 25%;
                                font-weight: 500;
                                vertical-align: middle;
                                border-top-left-radius: 8px;
                                border-bottom-left-radius: 8px;
                            ">
                                <div style="display: flex; align-items: center;">
                                    <span style="
                                        display: inline-block;
                                        width: 14px;
                                        height: 14px;
                                        background-color: ${d.color};
                                        border-radius: 50%;
                                        margin-right: 12px;
                                        box-shadow: 0 0 0 2px rgba(var(--text-rgb), 0.1);
                                    "></span>
                                    <span>${d.title}</span>
                                </div>
                            </td>
                            <td style="
                                border: none;
                                padding: 1rem;
                                color: var(--text-muted);
                                font-size: 0.95em;
                                width: 60%;
                                vertical-align: middle;
                            ">
                                ${this.getSimpleDescription(d.title)}
                            </td>
                            <td class="value-cell" data-value="${d.value}" style="
                                border: none;
                                padding: 1rem;
                                color: var(--text-color);
                                font-weight: 600;
                                text-align: right;
                                vertical-align: middle;
                                border-top-right-radius: 8px;
                                border-bottom-right-radius: 8px;
                            ">
                                0
                            </td>
                        </tr>
                    `
											)
											.join("")}
                </tbody>
            </table>
        </div>
    `;

		// Append the calculation details after the funnel
		$(calculationHTML).insertAfter(this.elements.funnel_wrapper);

		// Animate the numbers in the table
		$(".calculation-table .value-cell").each((i, cell) => {
			const $cell = $(cell);
			const finalValue = parseInt($cell.data("value"));
			this.animate_number(0, finalValue, 300, (value) => {
				$cell.text(value);
			});
		});

		// Add hover effect
		$(".calculation-table tr").hover(
			function () {
				$(this).css({
					background: "var(--fg-hover-color)",
					transform: "scale(1.01)",
					"box-shadow": "0 4px 8px rgba(0,0,0,0.1)",
				});
			},
			function () {
				$(this).css({
					background: "var(--fg-color)",
					transform: "scale(1)",
					"box-shadow": "none",
				});
			}
		);
	}

	redrawFunnel(hoveredIndex = null) {
		requestAnimationFrame(() => {
			this.labels = [];
			const context = this.elements.context;
			const max_width = this.options.width * 0.6;
			const min_width = max_width * 0.2;
			let y = 20;

			context.clearRect(0, 0, this.options.width, this.options.height);

			if (!this.options.data || !this.options.data.length) {
				this.elements.no_data.toggle(true);
				return;
			}

			const funnel_offset = this.options.width * 0.05;

			// Draw with animation
			this.options.data.forEach((d, i) => {
				const isLastTwoSections = i >= this.options.data.length - 2;

				// Calculate widths with curved reduction
				let current_width, next_width;

				if (isLastTwoSections) {
					current_width = min_width * 1.5;
					next_width = min_width * 1.5;
				} else {
					const progress = i / (this.options.data.length - 2);
					current_width = max_width * (1 - progress * 0.7);
					next_width = max_width * (1 - ((i + 1) / (this.options.data.length - 2)) * 0.7);
				}

				const x_start = funnel_offset + (max_width - current_width) / 2;
				const x_end = x_start + current_width;
				const next_x_start = funnel_offset + (max_width - next_width) / 2;
				const next_x_end = next_x_start + next_width;

				const current_y = y;
				const next_y = y + d.height;

				const x_mid = (x_start + x_end) / 2;
				const y_mid = y + d.height / 2;

				// Set fill style with opacity for smooth transition
				context.fillStyle = d.color;

				if (i === hoveredIndex) {
					context.save();
					context.shadowColor = "rgba(0, 0, 0, 0.5)";
					context.shadowBlur = 15;
					context.fillStyle = this.adjustColor(d.color, 20);
				}

				// Draw funnel section
				context.beginPath();
				context.moveTo(x_start, current_y);
				context.lineTo(x_end, current_y);

				if (isLastTwoSections) {
					context.lineTo(x_end, next_y);
					context.lineTo(x_start, next_y);
				} else {
					context.lineTo(next_x_end, next_y);
					context.lineTo(next_x_start, next_y);
				}

				context.closePath();
				context.fill();

				if (i === hoveredIndex) {
					context.restore();
				}

				// Draw legend
				this.draw_legend(
					x_mid,
					y_mid,
					this.options.width,
					this.options.height,
					d.value + " - " + d.title,
					i === hoveredIndex
				);

				y += d.height;
			});
		});
	}

	prepare_funnel() {
		const isMobile = window.innerWidth <= 768;
		const wrapperWidth = $(this.elements.funnel_wrapper).width();

		this.options.width = isMobile ? wrapperWidth : wrapperWidth;
		this.options.height = this.options.width * 0.55;

		var me = this;
		this.elements.no_data.toggle(false);

		const total_value = this.options.data.reduce((sum, d) => sum + d.value, 0);
		const total_height = this.options.height - 20;

		$.each(this.options.data, function (i, d) {
			d.height = (d.value / total_value) * total_height * 0.9;
		});

		this.elements.funnel_wrapper.empty();
		this.elements.canvas = $("<canvas></canvas>")
			.appendTo(this.elements.funnel_wrapper)
			.attr("width", this.options.width)
			.attr("height", this.options.height);
		this.elements.context = this.elements.canvas.get(0).getContext("2d");
	}

	adjustColor(color, percent) {
		const num = parseInt(color.slice(1), 16);
		const amt = Math.round(2.55 * percent);
		const rgb = [
			Math.min(255, Math.max(0, (num >> 16) + amt)),
			Math.min(255, Math.max(0, ((num >> 8) & 0xff) + amt)),
			Math.min(255, Math.max(0, (num & 0xff) + amt)),
		];
		return "#" + rgb.map((x) => x.toString(16).padStart(2, "0")).join("");
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

		// Calculate percentage
		const total = this.options.data[0].value;
		const value = parseInt(title.split(" - ")[0]);
		const percentage = ((value / total) * 100).toFixed(1);
		const titleParts = title.split(" - ");
		const labelText = titleParts[1];

		context.fillStyle = getComputedStyle(document.body).getPropertyValue("--text-color");
		context.textBaseline = "middle";
		context.font = isHovered ? "bold 1.1em sans-serif" : "1em sans-serif";

		const labelHeight = parseInt(context.font);
		const labels = this.labels || (this.labels = []);

		// Check for collisions and adjust position
		const minLabelSpacing = isHovered ? 35 : 25;
		let adjustedY = y_mid;
		let collision = true;
		while (collision) {
			collision = false;
			for (let label of labels) {
				if (Math.abs(label.y - adjustedY) < minLabelSpacing) {
					adjustedY += minLabelSpacing;
					collision = true;
					break;
				}
			}
		}

		labels.push({ y: adjustedY });

		// Animate the number if it's a new value or has changed
		const key = `${line_end}-${adjustedY}`;
		if (!this._animatedValues) this._animatedValues = {};

		if (this._animatedValues[key] !== value) {
			const startValue = 0;
			this.animate_number(startValue, value, 300, (currentValue) => {
				context.clearRect(line_end + 15, adjustedY - 15, 200, 30);
				context.fillText(
					`${currentValue} - ${labelText} (${((currentValue / total) * 100).toFixed(1)}%)`,
					line_end + 15,
					adjustedY
				);
			});
			this._animatedValues[key] = value;
		} else {
			context.fillText(__(title + ` (${percentage}%)`), line_end + 15, adjustedY);
		}
	}

	destroy() {
		$(window).off("resize", this.debouncedRender);
		this.elements.canvas?.off("mousemove mouseout");
		this._descriptions = null;
		this.elements = null;
	}
};

function isPointInTrapezoid(x, y, points) {
	let inside = false;
	const len = points.length;
	for (let i = 0, j = len - 1; i < len; j = i++) {
		const xi = points[i].x;
		const yi = points[i].y;
		const xj = points[j].x;
		const yj = points[j].y;

		if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
			inside = !inside;
		}
	}
	return inside;
}
