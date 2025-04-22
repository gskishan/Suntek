frappe.ui.form.on("Site Survey", {
    onload: function (frm) {
        if (frm.is_new()) {
            frm.call({
                method: "set_site_engineer",
                doc: frm.doc,
                callback: function (r) {
                    if (r.message) {
                        user = r.message.user;
                        employee = r.message.employee;

                        if (user) {
                            frm.set_value("custom_site_visitor", user.name);
                        }

                        if (employee) {
                            frm.set_value("site_engineer", employee.name);
                        }
                    }
                },
            });
        }
    },
    refresh: function (frm) {
        if (frm.is_new()) {
            frappe.call({
                method: "get_opportunity_details",
                doc: frm.doc,
                callback: function (e) {
                    cur_frm.refresh_fields();

                    if (!frm.doc.location) {
                        checkLocationPermissionAndCapture(frm);
                    }
                },
            });
        }

        if (!frm.doc.location) {
            frm.add_custom_button(__("Capture Location"), function () {
                checkLocationPermissionAndCapture(frm);
            }).addClass("btn-primary");
        }

        frm.add_custom_button(
            __("Designing"),
            function () {
                frappe.model.with_doctype("Designing", function () {
                    var DesigningDoc = frappe.model.get_new_doc("Designing");
                    DesigningDoc.designer = frm.doc.site_engineer;
                    DesigningDoc.site_survey = frm.doc.name;
                    DesigningDoc.opportunity_name = frm.doc.opportunity_name;
                    DesigningDoc.designing_status = "Open";

                    DesigningDoc.customer_name = frm.doc.customer_name;
                    DesigningDoc.customer_number = frm.doc.customer_number;
                    DesigningDoc.opportuniy_owner = frm.doc.opportunity_owner;
                    DesigningDoc.sales_person = frm.doc.sales_person;
                    DesigningDoc.poc_name = frm.doc.poc_name;
                    DesigningDoc.poc_contact = frm.doc.poc_contact;

                    frappe.set_route("Form", "Designing", DesigningDoc.name);
                });
            },
            __("Create"),
        );
        frm.fields_dict["site_engineer"].get_query = function (doc, cdt, cdn) {
            return {
                filters: {
                    department: frm.doc.department,
                },
            };
        };
        frm.fields_dict["department"].df.onchange = function () {
            frm.set_value("site_engineer", "");
            frm.refresh_field("site_engineer");
        };

        frm.trigger_enter_location_manually = function () {
            showManualLocationDialog(frm);
        };
    },

    validate: function (frm) {
        if (!frm.doc.location) {
            frappe.msgprint({
                title: __("Location Required"),
                indicator: "red",
                message: __("Please capture location to continue. This is required for Site Survey."),
            });
            return false;
        }
        return true;
    },
});

function checkLocationPermissionAndCapture(frm) {
    if (!navigator.geolocation) {
        frappe.msgprint(__("Geolocation is not supported by this browser"));
        return;
    }

    frappe.show_alert({
        message: __("Requesting location access..."),
        indicator: "blue",
    });

    if (navigator.permissions && navigator.permissions.query) {
        navigator.permissions
            .query({ name: "geolocation" })
            .then((permissionStatus) => {
                if (permissionStatus.state === "granted") {
                    captureLocation(frm);
                } else if (permissionStatus.state === "prompt") {
                    captureLocation(frm);
                } else if (permissionStatus.state === "denied") {
                    showEnableLocationInstructions();
                }

                permissionStatus.onchange = function () {
                    if (this.state === "granted") {
                        captureLocation(frm);
                    }
                };
            })
            .catch((error) => {
                captureLocation(frm);
            });
    } else {
        captureLocation(frm);
    }
}

function showEnableLocationInstructions() {
    const browserName = getBrowserName();
    let instructions = "";

    if (browserName === "Chrome" || browserName === "Edge") {
        instructions = `
            To enable location access in ${browserName}:
            <ol>
                <li>Click the lock/info icon in the address bar</li>
                <li>Click on "Site settings"</li>
                <li>Under "Permissions", set "Location" to "Allow"</li>
                <li>Refresh the page and try again</li>
            </ol>
        `;
    } else if (browserName === "Firefox") {
        instructions = `
            To enable location access in Firefox:
            <ol>
                <li>Click the lock/info icon in the address bar</li>
                <li>Click the "x" next to "Block" for Location</li>
                <li>Refresh the page and try again</li>
            </ol>
        `;
    } else if (browserName === "Safari") {
        instructions = `
            To enable location access in Safari:
            <ol>
                <li>Open Safari Preferences</li>
                <li>Go to the "Websites" tab</li>
                <li>Select "Location" on the left</li>
                <li>Find this website and set permission to "Allow"</li>
                <li>Refresh the page and try again</li>
            </ol>
        `;
    } else {
        instructions = `
            To enable location access:
            <ol>
                <li>Check your browser settings</li>
                <li>Look for location permissions</li>
                <li>Enable location access for this website</li>
                <li>Refresh the page and try again</li>
            </ol>
        `;
    }

    frappe.msgprint({
        title: __("Location Permission Required"),
        message: __(instructions),
        indicator: "red",
    });
}

function getBrowserName() {
    const userAgent = navigator.userAgent;
    let browserName;

    if (userAgent.match(/chrome|chromium|crios/i)) {
        browserName = "Chrome";
    } else if (userAgent.match(/firefox|fxios/i)) {
        browserName = "Firefox";
    } else if (userAgent.match(/safari/i)) {
        browserName = "Safari";
    } else if (userAgent.match(/opr\//i)) {
        browserName = "Opera";
    } else if (userAgent.match(/edg/i)) {
        browserName = "Edge";
    } else {
        browserName = "Unknown";
    }

    return browserName;
}

function captureLocation(frm) {
    navigator.geolocation.getCurrentPosition(
        function (position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
            console.log(`Accuracy: ${accuracy} meters`);

            if (isValidCoordinate(latitude) && isValidCoordinate(longitude)) {
                const googleMapsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;
                console.log(`Google Maps URL: ${googleMapsUrl}`);

                frm.set_value("custom_google_map_location", googleMapsUrl);

                const locationString = JSON.stringify({
                    type: "FeatureCollection",
                    features: [
                        {
                            type: "Feature",
                            properties: {
                                name: "Current Location",
                                radius: Math.min(accuracy, 100),
                            },
                            geometry: {
                                type: "Point",
                                coordinates: [longitude, latitude],
                            },
                        },
                        {
                            type: "Feature",
                            properties: {
                                name: "Coverage Area",
                                radius: 100,
                                stroke: "#3388ff",
                                "stroke-width": 2,
                                "stroke-opacity": 0.8,
                                fill: "#3388ff",
                                "fill-opacity": 0.2,
                            },
                            geometry: {
                                type: "Point",
                                coordinates: [longitude, latitude],
                            },
                        },
                    ],
                });

                frm.doc.location = locationString;
                frm.refresh_field("location");
                frm.refresh_field("custom_google_map_location");

                const message = `
                    <div>
                        <p><strong>Coordinates:</strong> ${latitude}, ${longitude}</p>
                        <p><strong>Accuracy:</strong> ${Math.round(accuracy)} meters</p>
                        <p><a href="${googleMapsUrl}" target="_blank">View on Google Maps</a></p>
                    </div>
                `;

                frappe.msgprint({
                    title: __("Location Captured"),
                    message: message,
                    indicator: "green",
                });

                frm.remove_custom_button(__("Capture Location"));
            } else {
                frappe.msgprint({
                    title: __("Invalid Coordinates"),
                    message: __("The coordinates received are invalid. Please try again or enter them manually."),
                    indicator: "red",
                });
            }
        },

        function (error) {
            console.error("Geolocation error:", error);

            if (error.code === error.PERMISSION_DENIED) {
                showEnableLocationInstructions();
            } else {
                let errorMessage = "";
                let isMacOS = navigator.platform.toUpperCase().indexOf("MAC") >= 0;

                switch (error.code) {
                    case error.POSITION_UNAVAILABLE:
                        if (isMacOS) {
                            errorMessage =
                                "Location information is unavailable. This is common on Mac computers as they rely on WiFi positioning instead of GPS. Please check that Location Services are enabled in System Settings and try again.";
                        } else {
                            errorMessage =
                                "Location information is unavailable. This may be due to GPS signal issues or device limitations.";
                        }
                        break;
                    case error.TIMEOUT:
                        if (isMacOS) {
                            errorMessage =
                                "The request to get location timed out. Mac computers often have difficulty determining precise locations. Please try in a different location.";
                        } else {
                            errorMessage =
                                "The request to get location timed out. Please try again in an area with better GPS signal.";
                        }
                        break;
                    default:
                        errorMessage = "An unknown error occurred while getting location.";
                        break;
                }

                frappe.msgprint({
                    title: __("Location Error"),
                    indicator: "red",
                    message: __(errorMessage),
                });
            }
        },

        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 60000,
        },
    );
}

function showManualLocationDialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __("Enter Location Manually"),
        fields: [
            {
                fieldname: "error_message",
                fieldtype: "HTML",
                options: `<div class="alert alert-warning">
                    ${__("Please enter your location coordinates manually.")}
                </div>`,
            },
            {
                label: __("Latitude"),
                fieldname: "latitude",
                fieldtype: "Float",
                precision: 8,
                reqd: 1,
                description: __("e.g. 17.4366"),
            },
            {
                label: __("Longitude"),
                fieldname: "longitude",
                fieldtype: "Float",
                precision: 8,
                reqd: 1,
                description: __("e.g. 78.3668"),
            },
            {
                label: __("Radius (meters)"),
                fieldname: "radius",
                fieldtype: "Int",
                default: 100,
                description: __("Area coverage radius in meters"),
            },
        ],
        primary_action_label: __("Set Location"),
        primary_action: function (values) {
            const latitude = values.latitude;
            const longitude = values.longitude;
            const radius = values.radius || 100;

            if (!isValidCoordinate(latitude) || !isValidCoordinate(longitude)) {
                frappe.throw(__("Please enter valid latitude and longitude values"));
                return;
            }

            const googleMapsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

            frm.set_value("custom_google_map_location", googleMapsUrl);

            const locationString = JSON.stringify({
                type: "FeatureCollection",
                features: [
                    {
                        type: "Feature",
                        properties: {
                            name: "Manual Location",
                        },
                        geometry: {
                            type: "Point",
                            coordinates: [longitude, latitude],
                        },
                    },
                    {
                        type: "Feature",
                        properties: {
                            name: "Coverage Area",
                            radius: radius,
                            stroke: "#3388ff",
                            "stroke-width": 2,
                            "stroke-opacity": 0.8,
                            fill: "#3388ff",
                            "fill-opacity": 0.2,
                        },
                        geometry: {
                            type: "Point",
                            coordinates: [longitude, latitude],
                        },
                    },
                ],
            });

            frm.doc.location = locationString;
            frm.refresh_field("location");
            frm.refresh_field("custom_google_map_location");

            frm.remove_custom_button(__("Capture Location"));

            frappe.show_alert({
                message: __("Location set manually"),
                indicator: "green",
            });

            d.hide();
        },
    });

    d.show();
}

function isValidCoordinate(value) {
    return (
        value !== null && value !== undefined && !isNaN(value) && value !== "" && value !== 0 && Math.abs(value) <= 180
    );
}
