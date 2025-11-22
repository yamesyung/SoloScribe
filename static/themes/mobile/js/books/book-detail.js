function showQuoteOverlay() {
    document.getElementById("quote-overlay").style.display = "block";
}

function closeQuoteOverlay() {
    document.getElementById('quote-overlay').style.display = 'none';
}

document.addEventListener('keyup', function(event) {
    if (event.key === "Escape") {
        closeQuoteOverlay();
    }
});

function adjustTextareaHeight(selector) {
    const textarea = document.querySelector(selector);
    if (!textarea) return;

    function autoGrow() {
        textarea.style.height = "auto";
        textarea.style.height = (textarea.scrollHeight + 40) + "px";
    }

    autoGrow();
    textarea.addEventListener("input", autoGrow);
}

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "quote-overlay") {
        var input = document.querySelector('.quoteTag');
        var button = input ? input.nextElementSibling : null;

        if (input && !input.dataset.tagifyInitialized) {
            // Initialize Tagify
            var tagify = new Tagify(input, {
                pattern: /^[^,]+$/,
                transformTag: function(tagData) {
                    tagData.value = tagData.value.replace(/\s+/g, '-');
                    return tagData;
                },
                editTags: {
                    keepInvalid: false,
                },
                validate: (tag) => {
                    const maxLength = 45;
                    if (tag.value.length > maxLength) {
                        tag.error = `Tag is too long (max ${maxLength} characters allowed)`;
                        return false;
                    }
                    return true;
                }
            });

            input.dataset.tagifyInitialized = "true";

            if (button) {
                button.addEventListener("click", function() {
                    tagify.addEmptyTag();
                });
            }

        }

    }
});

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "quote-overlay") {

        function initTagify(selector, pattern = /^[^,]+$/) {
            const input = document.querySelector(selector);
            const button = input ? input.nextElementSibling : null;

            if (input && !input.dataset.tagifyInitialized) {
                const tagify = new Tagify(input, {
                    pattern: pattern,
                    editTags: {
                        keepInvalid: false,
                    },
                    validate: (tag) => {
                        const maxLength = 45;
                        if (tag.value.length > maxLength) {
                            tag.error = `Tag is too long (max ${maxLength} characters allowed)`;
                            return false;
                        }
                        return true;
                    }
                });

                input.dataset.tagifyInitialized = "true";

                if (button) {
                    button.addEventListener("click", function() {
                        tagify.addEmptyTag();
                    });
                }
            }
        }

        initTagify('.genresTagify');
        initTagify('.tagsTagify');
    }
});


document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "review-wrapper") {
        var reviewBtn = document.getElementById('review-btn');
        var reviewContent = document.getElementById('review-wrapper')

         if (reviewContent && reviewContent.textContent.trim() !== "") {
            reviewBtn.innerText = "Edit review";
        } else {
            reviewBtn.innerText = "Add review";
        }
    }
});


var picker = new Pikaday({
    field: document.getElementById('date-read'),
    format: 'YYYY MMM D',
    minDate: new Date(2000, 0, 1),
    maxDate: new Date(2029, 11, 31),
    firstDay: 1,
    trigger: document.getElementById('calendar-icon'),
    onSelect: function(date) {
        var dateField = document.getElementById('date-read');
        var dateButton = document.getElementById('date-button');

        //format twice, one for backend, one for text display
        var options = { year: 'numeric', month: 'short', day: 'numeric' };
        var formattedButtonDate = date.toLocaleDateString('en-US', options);

        var year = date.getFullYear();
        var month = (date.getMonth() + 1).toString().padStart(2, '0');
        var day = date.getDate().toString().padStart(2, '0');

        var formattedDate = `${year}-${month}-${day}`;
        dateField.value = formattedDate;
        dateButton.textContent = 'Set to: ' + formattedButtonDate;
        dateButton.style.display = 'block';
        dateButton.setAttribute('hx-vals', JSON.stringify({ date: formattedDate }));
    }
 });


document.addEventListener('DOMContentLoaded', function() {

    const colorThief = new ColorThief();
    const bookCover = document.querySelector('#book-cover img');
    const personalInfo = document.getElementById('book-personal-info');

    if (bookCover && personalInfo) {
        const img = new Image();
        img.src = bookCover.src;

        img.addEventListener('load', function() {
            try {
                const palette = colorThief.getPalette(img, 3);
                if (palette && palette.length >= 2) {
                    const color1 = `rgb(${palette[0][0]}, ${palette[0][1]}, ${palette[0][2]})`;
                    const color2 = `rgb(${palette[1][0]}, ${palette[1][1]}, ${palette[1][2]})`;
                    document.body.style.background = `linear-gradient(135deg, ${color1} 0%, ${color2} 100%)`;
                }
            } catch (e) {
                console.log('Color extraction skipped');
            }
        });
    }

});


// Create and inject mobile menu button
(function() {
    // Create the button element
    const menuButton = document.createElement('button');
    menuButton.id = 'mobile-menu-toggle';
    menuButton.className = 'mobile-menu-btn';
    menuButton.innerHTML = '⚙';
    menuButton.setAttribute('aria-label', 'Toggle menu');

    // Add button to the page (top right)
    document.body.appendChild(menuButton);

    // Get the buttons container
    const buttonsContainer = document.getElementById('buttons-container');
    const dangerButtons = document.getElementById('danger-buttons');

    // Create a wrapper for both containers if they need to be grouped
    let menuWrapper = document.getElementById('mobile-menu-wrapper');
    if (!menuWrapper) {
        menuWrapper = document.createElement('div');
        menuWrapper.id = 'mobile-menu-wrapper';
        menuWrapper.className = 'mobile-menu-hidden';

        // Wrap both containers
        if (buttonsContainer) {
            buttonsContainer.parentNode.insertBefore(menuWrapper, buttonsContainer);
            menuWrapper.appendChild(buttonsContainer);
        }
        if (dangerButtons) {
            menuWrapper.appendChild(dangerButtons);
        }
    }

    // Toggle menu visibility
    menuButton.addEventListener('click', function(e) {
        e.stopPropagation();
        menuWrapper.classList.toggle('mobile-menu-hidden');
        menuWrapper.classList.toggle('mobile-menu-visible');
        document.body.classList.toggle('menu-open');

        // Change icon
        if (menuWrapper.classList.contains('mobile-menu-visible')) {
            menuButton.innerHTML = '✕'; // Close icon
        } else {
            menuButton.innerHTML = '⚙';
        }
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!menuWrapper.contains(e.target) && e.target !== menuButton) {
            menuWrapper.classList.remove('mobile-menu-visible');
            menuWrapper.classList.add('mobile-menu-hidden');
            document.body.classList.remove('menu-open');
            menuButton.innerHTML = '⚙';
        }
    });

    menuWrapper.addEventListener('click', function(e) {
        // Check if clicked element is a button or inside a button
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            menuWrapper.classList.remove('mobile-menu-visible');
            menuWrapper.classList.add('mobile-menu-hidden');
            document.body.classList.remove('menu-open');
            menuButton.innerHTML = '⚙';
        } else {
            // Prevent other clicks from closing the menu
            e.stopPropagation();
        }
    });
})();