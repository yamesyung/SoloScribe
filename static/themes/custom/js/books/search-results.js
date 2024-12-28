  document.addEventListener("DOMContentLoaded", function () {
    const colorThief = new ColorThief();
    const resultItems = document.querySelectorAll(".search-result-item");

    resultItems.forEach((item) => {
      const img = item.querySelector(".cover-image");
      if (img.complete) {
        applyBackground(img, item);
      } else {
        img.addEventListener("load", () => applyBackground(img, item));
      }
    });

    function applyBackground(img, item) {
      try {
        const colors = colorThief.getPalette(img, 2);
        const gradient = `linear-gradient(to right, rgba(21, 27, 35, 0), rgb(${colors[0]}))`;
        item.style.background = gradient;
        item.style.color = "white";
      } catch (e) {
        console.error("Color extraction failed:", e);
      }
    }
  });