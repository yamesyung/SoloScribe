function closeOverlay() {
    const overlay = document.getElementById("setting-form-content");
    if (overlay) {
        overlay.style.display = "none";
    }
}

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        closeOverlay();
    }
});