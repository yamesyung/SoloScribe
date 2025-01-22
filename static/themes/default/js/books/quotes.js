let masonryInstance = new Masonry('#grid', {
    columnWidth: '.quote-container',
    itemSelector: '.quote-container',
    percentPosition: true,
    gutter: 20
});

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "grid") {
        setTimeout(() => {
            masonryInstance.reloadItems();
            masonryInstance.layout();
        }, 100);
    }
});