// Function to inject GTM and GA scripts (high in head)
function injectEarlyHeadScripts() {
	// Google Tag Manager
	var gtmScript = document.createElement("script");
	gtmScript.text = `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,'script','dataLayer','GTM-T452DBWT');`;
	document.head.insertBefore(gtmScript, document.head.firstChild);

	// Google Analytics
	var gaScriptSrc = document.createElement("script");
	gaScriptSrc.async = true;
	gaScriptSrc.src = "https://www.googletagmanager.com/gtag/js?id=G-KFS9KH8LC7";
	document.head.appendChild(gaScriptSrc);

	var gaScript = document.createElement("script");
	gaScript.text = `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-KFS9KH8LC7');
  `;
	document.head.appendChild(gaScript);
}

// Function to inject Meta Pixel (just before </head>)
function injectMetaPixel() {
	var fbScript = document.createElement("script");
	fbScript.text = `
      !function(f,b,e,v,n,t,s)
      {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
      n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
      n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s)}(window, document,'script',
      'https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', '1385332509097665');
      fbq('track', 'PageView');
  `;
	// Append to end of head
	document.head.appendChild(fbScript);
}

// Function to inject body scripts
function injectBodyScripts() {
	// Google Tag Manager noscript
	var noscript = document.createElement("noscript");
	var iframe = document.createElement("iframe");
	iframe.src = "https://www.googletagmanager.com/ns.html?id=GTM-T452DBWT";
	iframe.height = "0";
	iframe.width = "0";
	iframe.style.display = "none";
	iframe.style.visibility = "hidden";
	noscript.appendChild(iframe);
	document.body.insertBefore(noscript, document.body.firstChild);

	// Facebook Pixel noscript
	var pixelNoscript = document.createElement("noscript");
	var pixelImg = document.createElement("img");
	pixelImg.height = "1";
	pixelImg.width = "1";
	pixelImg.style.display = "none";
	pixelImg.src = "https://www.facebook.com/tr?id=1385332509097665&ev=PageView&noscript=1";
	pixelNoscript.appendChild(pixelImg);
	document.body.appendChild(pixelNoscript);
}

function setupFormTracking() {
	// Wait for the form to be available using the correct selector
	const formSelector = 'form.web-form[role="form"]';

	// Use MutationObserver to detect when the form is added to the DOM
	const observer = new MutationObserver(function (mutations) {
		const form = document.querySelector(formSelector);
		if (form) {
			observer.disconnect(); // Stop observing once form is found

			form.addEventListener("submit", function (event) {
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
						content_name: "Contact Us Form",
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

	// Start observing the document with the configured parameters
	observer.observe(document.body, {
		childList: true,
		subtree: true,
	});
}

// Modify your existing execution code to include form tracking
if (document.readyState === "loading") {
	injectEarlyHeadScripts(); // GTM and GA first
	document.addEventListener("DOMContentLoaded", function () {
		injectMetaPixel(); // Meta Pixel just before </head>
		injectBodyScripts(); // Body scripts after DOM is ready
		setupFormTracking(); // Add form tracking
	});
} else {
	injectEarlyHeadScripts();
	injectMetaPixel();
	injectBodyScripts();
	setupFormTracking();
}
