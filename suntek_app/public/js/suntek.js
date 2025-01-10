// Google Tag Manager
(function (w, d, s, l, i) {
	w[l] = w[l] || [];
	w[l].push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
	var f = d.getElementsByTagName(s)[0],
		j = d.createElement(s),
		dl = l != "dataLayer" ? "&l=" + l : "";
	j.async = true;
	j.src = "https://www.googletagmanager.com/gtm.js?id=" + i + dl;
	f.parentNode.insertBefore(j, f);
})(window, document, "script", "dataLayer", "GTM-NQTF7J7D");

// Add GTM noscript iframe
document.addEventListener("DOMContentLoaded", function () {
	// Create noscript element
	var noscript = document.createElement("noscript");

	// Create iframe
	var iframe = document.createElement("iframe");
	iframe.src = "https://www.googletagmanager.com/ns.html?id=GTM-NQTF7J7D";
	iframe.height = "0";
	iframe.width = "0";
	iframe.style.display = "none";
	iframe.style.visibility = "hidden";

	// Add iframe to noscript
	noscript.appendChild(iframe);

	// Insert after body tag
	document.body.insertBefore(noscript, document.body.firstChild);
});
