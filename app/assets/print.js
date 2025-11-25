// assets/print.js
(function () {

  const HTML2CANVAS_URL =
    "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
  const JSPDF_URL =
    "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";

  function loadScript(url) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = url;
      s.onload = resolve;
      s.onerror = () => reject(new Error("Failed to load " + url));
      document.head.appendChild(s);
    });
  }

  async function init() {
    // Load libs
    if (typeof html2canvas === "undefined") {
      await loadScript(HTML2CANVAS_URL);
    }

    if (typeof window.jspdf === "undefined") {
      await loadScript(JSPDF_URL);
    }

    const { jsPDF } = window.jspdf;

    // Attach listener
    function attach() {
      const btn = document.getElementById("btn-print");
      if (!btn) return; // if button not yet in DOM

      btn.addEventListener("click", async () => {
        const orig = btn.innerText;
        btn.disabled = true;
        btn.innerText = "Generating...";

        try {
          const canvas = await html2canvas(document.body, {
            scale: 2,
            useCORS: true,
          });

          const imgData = canvas.toDataURL("image/jpeg", 0.95);

          const pdf = new jsPDF("p", "mm", "a4");
          const pdfWidth = 210;
          const pdfHeight = 297;

          const imgWidth = pdfWidth;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;

          let y = 0;
          let pageHeightLeft = imgHeight;

          pdf.addImage(imgData, "JPEG", 0, 0, imgWidth, imgHeight);

          // Add pages if long
          while (pageHeightLeft > pdfHeight) {
            pdf.addPage();
            y -= pdfHeight;
            pdf.addImage(imgData, "JPEG", 0, y, imgWidth, imgHeight);
            pageHeightLeft -= pdfHeight;
          }

          pdf.save("storyboard.pdf");
        } catch (e) {
          console.error(e);
          alert("Failed to create PDF. Open console for details.");
        }

        btn.disabled = false;
        btn.innerText = orig;
      });
    }

    // Attach on startup
    attach();

    // Re-attach if dash re-mounts the layout (important!)
    new MutationObserver(() => attach()).observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  // Start the script
  init();
})();
