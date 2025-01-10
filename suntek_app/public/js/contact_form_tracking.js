frappe.ready(function () {
	// This code will only run on the contact-us web form
	if (frappe.web_form.name === "contact-us") {
		// Track form submission
		frappe.web_form.on("submit", function (event) {
			// Google Analytics Event
			if (typeof gtag === "function") {
				gtag("event", "form_submission", {
					event_category: "Contact Form",
					event_label: "Contact Us Form Submit",
					page_url: window.location.href,
				});
			}

			// Facebook Pixel Event
			if (typeof fbq === "function") {
				fbq("track", "Lead", {
					content_name: "Contact Form",
					page_url: window.location.href,
				});
			}

			// Google Tag Manager Event
			if (typeof dataLayer !== "undefined") {
				dataLayer.push({
					event: "form_submission",
					form_name: "contact_us",
					form_type: "Contact Form",
					page_url: window.location.href,
				});
			}
		});
	}
});
