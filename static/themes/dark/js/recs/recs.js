//htmx.config.globalViewTransitions = true;

document.body.addEventListener("htmx:afterSwap", function(event) {
    // Add event listener for change events on .book-checkbox elements
    event.detail.elt.querySelectorAll('.book-checkbox').forEach(function(checkbox) {
        checkbox.addEventListener('change', function(event) {
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
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll(".cat-btn");

    buttons.forEach(button => {
        button.addEventListener("click", function() {
            const target = document.querySelector(button.getAttribute("data-target"));
            target.classList.toggle("show");
            const arrow = button.querySelector(".arrow");
            arrow.classList.toggle("rotate");
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const links = document.querySelectorAll(".list-links a");

    links.forEach(link => {
        link.addEventListener("click", function() {
            links.forEach(l => l.classList.remove("active-link"));
            this.classList.add("active-link");
        });
    });
});