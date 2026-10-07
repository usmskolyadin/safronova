document.addEventListener("DOMContentLoaded", function () {
  var revealTargets = document.querySelectorAll(
    ".section-heading, .hub-tile, .card, .about-block, .gallery-item, .page-header > .container"
  );

  if ("IntersectionObserver" in window && revealTargets.length) {
    var groups = new Map();
    revealTargets.forEach(function (el) {
      var parent = el.parentElement;
      if (!groups.has(parent)) {
        groups.set(parent, []);
      }
      groups.get(parent).push(el);
    });

    groups.forEach(function (siblings) {
      siblings.forEach(function (el, i) {
        el.style.setProperty("--reveal-delay", Math.min(i * 0.08, 0.4) + "s");
        el.classList.add("reveal");
      });
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    revealTargets.forEach(function (el) {
      observer.observe(el);
    });
  }

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      nav.classList.toggle("is-open");
    });
  }

  var dropdown = document.querySelector(".nav-dropdown");
  if (dropdown) {
    var dropdownLink = dropdown.querySelector("a");
    dropdownLink.addEventListener("click", function (e) {
      if (window.innerWidth <= 760) {
        e.preventDefault();
        dropdown.classList.toggle("is-open");
      }
    });
  }

  var lightbox = document.querySelector(".lightbox");
  if (lightbox) {
    var lightboxImg = lightbox.querySelector("img");
    var lightboxCaption = lightbox.querySelector(".lightbox-caption");
    var closeBtn = lightbox.querySelector(".lightbox-close");

    document.querySelectorAll("[data-lightbox]").forEach(function (item) {
      item.addEventListener("click", function () {
        lightboxImg.src = item.getAttribute("data-lightbox");
        lightboxCaption.textContent = item.getAttribute("data-caption") || "";
        lightbox.classList.add("is-open");
      });
    });

    function closeLightbox() {
      lightbox.classList.remove("is-open");
      lightboxImg.src = "";
    }

    closeBtn.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) {
        closeLightbox();
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        closeLightbox();
      }
    });
  }
});
