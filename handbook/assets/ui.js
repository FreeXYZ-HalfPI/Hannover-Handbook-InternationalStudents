/* SPDX-License-Identifier: GPL-3.0-or-later */
/* Copyleft 🄯 2026 ISL and contributors — makes the search easy to find, especially on phones:
   (1) every [data-isl-search] button (home page) opens the theme's search,
   (2) a floating «Search» button on every page. */
(function () {
  function openSearch() {
    var toggle = document.querySelector("[data-md-toggle=search]");
    var input = document.querySelector(".md-search__input");
    if (!toggle || !input) return;
    toggle.checked = true;
    toggle.dispatchEvent(new Event("change", { bubbles: true }));
    /* focus inside the click handler: iOS only opens the keyboard for focus that follows a tap */
    input.focus();
  }

  function init() {
    if (!document.querySelector(".md-search__input")) return;
    document.querySelectorAll("[data-isl-search]").forEach(function (el) {
      el.addEventListener("click", openSearch);
    });
    if (document.querySelector(".isl-fab")) return;
    var fab = document.createElement("button");
    fab.type = "button";
    fab.className = "isl-fab";
    fab.setAttribute("aria-label", "Search the handbook");
    fab.innerHTML = '<span aria-hidden="true">🔍</span><span class="isl-fab__text">Search</span>';
    fab.addEventListener("click", openSearch);
    document.body.appendChild(fab);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
