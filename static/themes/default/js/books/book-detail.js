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

function adjustTextareaHeight() {
    var reviewTextarea = document.getElementById("quote-input");

    function autoGrowTextarea() {
        reviewTextarea.style.height = "auto";
        reviewTextarea.style.height = (reviewTextarea.scrollHeight + 40) + "px";
    }

    autoGrowTextarea();
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