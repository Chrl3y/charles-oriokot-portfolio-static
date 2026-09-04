(function () {
  "use strict";
  var year = document.getElementById("current-year");
  if (year) year.textContent = String(new Date().getFullYear());
  var nav = document.getElementById("ftco-nav");
  if (nav) {
    nav.addEventListener("click", function (event) {
      var link = event.target.closest("a.nav-link[href^='#']");
      if (!link) return;

      var target = document.querySelector(link.getAttribute("href"));
      if (!target) return;

      event.preventDefault();
      event.stopImmediatePropagation();

      var completeNavigation = function () {
        var toggle = document.querySelector(".navbar-toggler");
        nav.classList.remove("show", "collapsing");
        nav.style.height = "";
        if (toggle) {
          toggle.classList.remove("active");
          toggle.setAttribute("aria-expanded", "false");
        }
        window.scrollTo(0, Math.max(0, target.offsetTop - 70));
        window.history.replaceState(null, "", link.getAttribute("href"));
      };

      if (window.innerWidth < 992) {
        window.jQuery(nav).collapse("hide");
        window.setTimeout(completeNavigation, 400);
      } else {
        completeNavigation();
      }
    });
  }
  // Contact form: no backend, so compose the message in the visitor's own mail
  // client instead of pretending to send it. Previously this alerted a
  // developer note, which read as a broken site to anyone who filled it in.
  // Belt and braces on the loader fix in custom.css: once the page has loaded
  // there is nothing left to show, so take the overlay out of the DOM entirely.
  window.addEventListener("load", function () {
    var loader = document.getElementById("ftco-loader");
    if (loader && loader.parentNode) loader.parentNode.removeChild(loader);
  });

  var field = function (id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : "";
  };

  var compose = function (subject, message, name, email, website) {
    var signoff = "\n\n\u2014\n" + name;
    if (email) signoff += "\n" + email;
    if (website) signoff += "\n" + website;
    window.location.href =
      "mailto:charleyfix47@gmail.com" +
      "?subject=" + encodeURIComponent(subject) +
      "&body=" + encodeURIComponent(message + signoff);
  };

  // index.html contact form.
  var contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", function (event) {
      event.preventDefault();
      compose(
        field("cf-subject") || "Portfolio enquiry",
        field("cf-message"),
        field("cf-name"),
        field("cf-email"),
        ""
      );
    });
  }

  // Article reply form. Subject carries the page title so replies are traceable
  // to the post they came from.
  var replyForm = document.getElementById("reply-form");
  if (replyForm) {
    replyForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var heading = document.querySelector("h1.bread");
      compose(
        "Reply: " + (heading ? heading.textContent.trim() : document.title),
        field("message"),
        field("name"),
        field("email"),
        field("website")
      );
    });
  }
})();
