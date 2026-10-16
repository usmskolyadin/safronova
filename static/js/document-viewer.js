(function () {
  "use strict";

  var PDF_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";
  var PDF_WORKER_URL = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
  var DOCX_PREVIEW_URL = "https://cdn.jsdelivr.net/npm/docx-preview@0.4.1/dist/docx-preview.min.js";

  var scriptPromises = {};
  function loadScript(src) {
    if (!scriptPromises[src]) {
      scriptPromises[src] = new Promise(function (resolve, reject) {
        var el = document.createElement("script");
        el.src = src;
        el.onload = function () {
          resolve();
        };
        el.onerror = function () {
          reject(new Error("Не удалось загрузить " + src));
        };
        document.head.appendChild(el);
      });
    }
    return scriptPromises[src];
  }

  var pdfJsReady = null;
  function ensurePdfJs() {
    if (!pdfJsReady) {
      pdfJsReady = loadScript(PDF_JS_URL).then(function () {
        window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDF_WORKER_URL;
      });
    }
    return pdfJsReady;
  }

  var docxReady = null;
  function ensureDocxPreview() {
    if (!docxReady) {
      docxReady = loadScript(DOCX_PREVIEW_URL);
    }
    return docxReady;
  }

  function createPageWrapper(contentEl, visible) {
    var wrapper = document.createElement("div");
    wrapper.className = "viewer-page";
    wrapper.style.display = visible ? "flex" : "none";
    var inner = document.createElement("div");
    inner.className = "viewer-page-inner";
    inner.appendChild(contentEl);
    wrapper.appendChild(inner);
    return wrapper;
  }

  function buildPdfPages(url, stageEl) {
    return ensurePdfJs().then(function () {
      return window.pdfjsLib.getDocument(url).promise;
    }).then(function (pdf) {
      var stageRect = stageEl.getBoundingClientRect();
      var pageNumbers = [];
      for (var i = 1; i <= pdf.numPages; i++) {
        pageNumbers.push(i);
      }
      var pages = [];
      function renderOne(num) {
        return pdf.getPage(num).then(function (page) {
          var baseViewport = page.getViewport({ scale: 1 });
          var scale = Math.min(
            stageRect.width / baseViewport.width,
            stageRect.height / baseViewport.height
          ) || 1;
          var pixelRatio = window.devicePixelRatio || 1;
          var viewport = page.getViewport({ scale: scale * pixelRatio });
          var canvas = document.createElement("canvas");
          canvas.width = viewport.width;
          canvas.height = viewport.height;
          canvas.style.width = (baseViewport.width * scale) + "px";
          canvas.style.height = (baseViewport.height * scale) + "px";
          var ctx = canvas.getContext("2d");
          return page.render({ canvasContext: ctx, viewport: viewport }).promise.then(function () {
            pages[num - 1] = createPageWrapper(canvas, num === 1);
          });
        });
      }
      var chain = Promise.resolve();
      pageNumbers.forEach(function (num) {
        chain = chain.then(function () {
          return renderOne(num);
        });
      });
      return chain.then(function () {
        return pages;
      });
    });
  }

  function buildDocxPages(url, stageEl) {
    return ensureDocxPreview().then(function () {
      return fetch(url).then(function (resp) {
        if (!resp.ok) {
          throw new Error("Не удалось загрузить файл");
        }
        return resp.arrayBuffer();
      });
    }).then(function (buffer) {
      var offscreen = document.createElement("div");
      offscreen.style.position = "absolute";
      offscreen.style.left = "-99999px";
      offscreen.style.top = "0";
      offscreen.style.visibility = "hidden";
      document.body.appendChild(offscreen);

      return window.docx.renderAsync(buffer, offscreen, null, {
        inWrapper: false,
        breakPages: true,
        ignoreLastRenderedPageBreak: false,
        experimental: true,
      }).then(function () {
        var stageRect = stageEl.getBoundingClientRect();
        var rawPages = Array.prototype.slice.call(offscreen.querySelectorAll(".docx"));

        if (!rawPages.length) {
          offscreen.style.position = "";
          offscreen.style.left = "";
          offscreen.style.top = "";
          offscreen.style.visibility = "";
          offscreen.style.width = "100%";
          offscreen.style.height = "100%";
          offscreen.style.overflow = "auto";
          offscreen.style.background = "#fff";
          document.body.removeChild(offscreen);
          return [createPageWrapper(offscreen, true)];
        }

        var pages = rawPages.map(function (pageEl, idx) {
          var w = pageEl.offsetWidth || 793;
          var h = pageEl.offsetHeight || 1122;
          var scale = Math.min(stageRect.width / w, stageRect.height / h) || 1;
          pageEl.style.transform = "scale(" + scale + ")";
          pageEl.style.transformOrigin = "top left";
          pageEl.style.margin = "0";
          var holder = document.createElement("div");
          holder.style.width = (w * scale) + "px";
          holder.style.height = (h * scale) + "px";
          holder.style.overflow = "hidden";
          holder.appendChild(pageEl);
          return createPageWrapper(holder, idx === 0);
        });

        document.body.removeChild(offscreen);
        return pages;
      });
    });
  }

  function initViewer() {
    var modal = document.getElementById("doc-viewer");
    if (!modal) {
      return;
    }

    var titleEl = modal.querySelector(".doc-viewer__title");
    var stageEl = modal.querySelector(".doc-viewer__stage");
    var statusEl = modal.querySelector(".doc-viewer__status");
    var closeBtn = modal.querySelector(".doc-viewer__close");
    var prevBtn = modal.querySelector(".doc-viewer__prev");
    var nextBtn = modal.querySelector(".doc-viewer__next");
    var currentIndicator = modal.querySelector(".doc-viewer__current");
    var totalIndicator = modal.querySelector(".doc-viewer__total");
    var downloadLink = modal.querySelector(".doc-viewer__download");

    var state = { pages: [], index: 0, animating: false };

    function updateIndicator() {
      currentIndicator.textContent = String(state.index + 1);
      totalIndicator.textContent = String(state.pages.length);
      prevBtn.disabled = state.index <= 0;
      nextBtn.disabled = state.index >= state.pages.length - 1;
      var showNav = state.pages.length > 1;
      prevBtn.style.visibility = showNav ? "visible" : "hidden";
      nextBtn.style.visibility = showNav ? "visible" : "hidden";
    }

    function goTo(direction) {
      if (state.animating) {
        return;
      }
      var nextIndex = state.index + direction;
      if (nextIndex < 0 || nextIndex >= state.pages.length) {
        return;
      }
      var current = state.pages[state.index];
      var target = state.pages[nextIndex];
      state.animating = true;

      target.style.display = "flex";

      if (direction > 0) {
        current.style.zIndex = "2";
        target.style.zIndex = "1";
        current.style.transformOrigin = "left center";
        current.style.transform = "rotateY(0deg)";
        requestAnimationFrame(function () {
          current.classList.add("is-flipping");
          current.style.transform = "rotateY(-180deg)";
        });
        bindEnd(current);
      } else {
        current.style.zIndex = "1";
        target.style.zIndex = "2";
        target.style.transformOrigin = "right center";
        target.style.transform = "rotateY(180deg)";
        requestAnimationFrame(function () {
          target.classList.add("is-flipping");
          target.style.transform = "rotateY(0deg)";
        });
        bindEnd(target);
      }

      function bindEnd(mover) {
        function onEnd(e) {
          if (e.target !== mover || e.propertyName !== "transform") {
            return;
          }
          mover.removeEventListener("transitionend", onEnd);
          mover.classList.remove("is-flipping");
          current.style.display = "none";
          current.style.transform = "";
          current.style.zIndex = "";
          target.style.transform = "";
          target.style.zIndex = "";
          state.index = nextIndex;
          state.animating = false;
          updateIndicator();
        }
        mover.addEventListener("transitionend", onEnd);
      }
    }

    function reset() {
      state.pages = [];
      state.index = 0;
      state.animating = false;
      stageEl.innerHTML = "";
      statusEl.style.display = "flex";
      statusEl.textContent = "Загрузка документа…";
    }

    function open(url, title) {
      reset();
      titleEl.textContent = title || "Просмотр документа";
      downloadLink.href = url;
      var fileName = url.split("/").pop().split("?")[0];
      downloadLink.setAttribute("download", fileName);
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
      document.documentElement.style.overflow = "hidden";

      var ext = (fileName.split(".").pop() || "").toLowerCase();
      var builder = ext === "pdf" ? buildPdfPages : (ext === "docx" || ext === "doc") ? buildDocxPages : null;

      if (!builder) {
        statusEl.textContent = "Предпросмотр недоступен для этого типа файла. Используйте кнопку «Скачать».";
        return;
      }

      builder(url, stageEl).then(function (pages) {
        if (!pages || !pages.length) {
          throw new Error("empty");
        }
        state.pages = pages;
        pages.forEach(function (p) {
          stageEl.appendChild(p);
        });
        statusEl.style.display = "none";
        updateIndicator();
      }).catch(function () {
        statusEl.textContent = "Не удалось показать предпросмотр этого файла. Используйте кнопку «Скачать».";
      });
    }

    function close() {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
      document.documentElement.style.overflow = "";
      reset();
    }

    closeBtn.addEventListener("click", close);
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        close();
      }
    });
    prevBtn.addEventListener("click", function () {
      goTo(-1);
    });
    nextBtn.addEventListener("click", function () {
      goTo(1);
    });
    document.addEventListener("keydown", function (e) {
      if (!modal.classList.contains("is-open")) {
        return;
      }
      if (e.key === "Escape") {
        close();
      } else if (e.key === "ArrowLeft") {
        goTo(-1);
      } else if (e.key === "ArrowRight") {
        goTo(1);
      }
    });

    var touchStartX = null;
    stageEl.addEventListener("touchstart", function (e) {
      touchStartX = e.changedTouches[0].clientX;
    });
    stageEl.addEventListener("touchend", function (e) {
      if (touchStartX === null) {
        return;
      }
      var dx = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(dx) > 50) {
        goTo(dx < 0 ? 1 : -1);
      }
      touchStartX = null;
    });

    document.addEventListener("click", function (e) {
      var trigger = e.target.closest ? e.target.closest("[data-doc-url]") : null;
      if (trigger) {
        e.preventDefault();
        open(trigger.getAttribute("data-doc-url"), trigger.getAttribute("data-doc-title"));
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initViewer);
  } else {
    initViewer();
  }
})();
