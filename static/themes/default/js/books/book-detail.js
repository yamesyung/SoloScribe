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
        var input = document.querySelector('.customLook');
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