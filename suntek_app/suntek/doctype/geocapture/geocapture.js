frappe.ui.form.on("Geocapture", {
  refresh: function (frm) {
    // Add a button to capture coordinates
    frm.add_custom_button(__("Capture & Print Location"), function () {
      checkLocationPermissionAndPrint();
    });
  },
});

function checkLocationPermissionAndPrint() {
  // First check if geolocation is supported
  if (!navigator.geolocation) {
    frappe.msgprint(__("Geolocation is not supported by this browser"));
    return;
  }

  // Modern browsers provide the permissions API to check status
  if (navigator.permissions && navigator.permissions.query) {
    navigator.permissions
      .query({ name: "geolocation" })
      .then((permissionStatus) => {
        if (permissionStatus.state === "granted") {
          // Permission already granted, proceed to get location
          printCurrentLocation();
        } else if (permissionStatus.state === "prompt") {
          // Permission hasn't been decided yet, will trigger the prompt
          printCurrentLocation();
        } else if (permissionStatus.state === "denied") {
          // Permission previously denied, show instructions to enable
          showEnableLocationInstructions();
        }

        // Set up listener for future permission changes
        permissionStatus.onchange = function () {
          if (this.state === "granted") {
            printCurrentLocation(); // print current location
          }
        };
      })
      .catch((error) => {
        // Fallback if permissions query fails
        printCurrentLocation();
      });
  } else {
    // Fallback for browsers without permissions API
    printCurrentLocation();
  }
}

function showEnableLocationInstructions() {
  const browserName = getBrowserName();
  let instructions;

  // Browser-specific instructions here...
  // (keeping the previous browser detection code)

  frappe.msgprint({
    title: __("Location Permission Required"),
    message: __(instructions),
    indicator: "red",
  });
}

function getBrowserName() {
  // Browser detection code here...
  // (keeping the previous browser detection code)
}

function printCurrentLocation() {
  navigator.geolocation.getCurrentPosition(
    // Success callback
    function (position) {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      // Create Google Maps URL
      const googleMapsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

      // Print coordinates to console
      console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
      console.log(`Google Maps URL: ${googleMapsUrl}`);

      // Create message with coordinates and clickable link
      const message = `
                <div>
                    <p><strong>Coordinates:</strong> ${latitude}, ${longitude}</p>
                    <p><a href="${googleMapsUrl}" target="_blank">View on Google Maps</a></p>
                </div>
            `;

      // Show the message with the link
      frappe.msgprint({
        title: __("Location Captured"),
        message: message,
        indicator: "green",
      });

      // Also show brief alert
      frappe.show_alert(
        {
          message: `Location captured successfully`,
          indicator: "green",
        },
        3,
      );

      // Optional: Create GeoJSON and print it too
      const geoJSON = {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            properties: {},
            geometry: {
              type: "Point",
              coordinates: [longitude, latitude],
            },
          },
        ],
      };

      console.log("GeoJSON:", geoJSON);
    },

    // Error callback
    function (error) {
      if (error.code === error.PERMISSION_DENIED) {
        showEnableLocationInstructions();
      } else {
        let errorMsg;
        switch (error.code) {
          case error.POSITION_UNAVAILABLE:
            errorMsg = "Location information is unavailable";
            break;
          case error.TIMEOUT:
            errorMsg = "Request to get location timed out";
            break;
          default:
            errorMsg = "An unknown error occurred while getting location";
        }
        frappe.msgprint(__(errorMsg));
      }
    },

    // Options
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    },
  );
}
