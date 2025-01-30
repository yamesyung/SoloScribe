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

document.body.addEventListener("htmx:afterSwap", function(event) {
    // Add event listener for change events on .book-checkbox elements
    event.detail.elt.querySelectorAll('.quote-fav').forEach(function(checkbox) {
        checkbox.addEventListener('change', function(event) {
            var checkboxId = event.target.id;
            // Get the corresponding book link element
            var quoteContainer = document.querySelector('#quote-' + checkboxId.split('-')[1]);

            // Check if the book link element exists
            if (quoteContainer) {
                // Check if the checkbox is checked and update the class of the book link accordingly
                if (event.target.checked) {
                    quoteContainer.classList.add('favorite');
                } else {
                    quoteContainer.classList.remove('favorite');
                }
            }
        });
    });
});