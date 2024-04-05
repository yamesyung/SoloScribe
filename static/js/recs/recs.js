

document.body.addEventListener("htmx:afterSwap", function(event) {
    // Add event listener for change events on .book-checkbox elements
    event.detail.elt.addEventListener('change', function(event) {
        // Check if the changed element is a .book-checkbox
        if (event.target.classList.contains('book-checkbox')) {
            var checkboxId = event.target.id;
            // Get the corresponding book link element
            var bookLink = document.querySelector('a#book-' + checkboxId.split('-')[1]);

            // Check if the book link element exists
            if (bookLink) {
                // Check if the checkbox is checked and update the class of the book link accordingly
                if (event.target.checked) {
                    bookLink.classList.add('read-book');
                } else {
                    bookLink.classList.remove('read-book');
                }
            }
        }
    });
});