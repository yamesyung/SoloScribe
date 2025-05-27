// Toggle left buttons
document.querySelectorAll('.cat-btn').forEach(button => {
    const targetId = button.getAttribute('data-target');
    const content = document.querySelector(targetId);
    const arrow = button.querySelector(".arrow");

    if (button.classList.contains('active')) {
        content.style.maxHeight = content.scrollHeight + 10 + "px";
        arrow.classList.add("rotate");
    }

    button.addEventListener('click', () => {
        button.classList.toggle('active');
        arrow.classList.toggle("rotate");

        if (button.classList.contains('active')) {
            content.style.maxHeight = content.scrollHeight + 10 + "px";
        } else {
            content.style.maxHeight = "0px";
        }
    });
});


function showOverlay() {
    document.getElementById("overlay").style.display = "block";
}


function closeOverlay() {
    document.getElementById('overlay').style.display = 'none'; // Hide overlay
}

function handleToggle() {
    const toggleCheckbox = document.getElementById("toggle-review-checkbox");
    const descriptionContent = document.getElementById("book-description");
    const reviewContent = document.getElementById("book-review");
    const reviewForm = document.getElementById("edit-review-container");

    if (toggleCheckbox.checked) {
        descriptionContent.classList.add("hidden");
        reviewContent.classList.remove("hidden");
    } else {
        descriptionContent.classList.remove("hidden");
        reviewContent.classList.add("hidden");

        if (reviewForm) {
            reviewForm.classList.add("hidden");
        }
    }
}

function handleToggleCancelEdit() {
    const reviewContent = document.getElementById("book-review");
    const reviewForm = document.getElementById("edit-review-container");

    reviewContent.classList.remove("hidden");
    reviewForm.classList.add("hidden");

}

function handleToggleAddReview() {
    const toggleCheckbox = document.getElementById("toggle-add-review-checkbox");
    const descriptionContent = document.getElementById("book-description");
    const reviewForm = document.getElementById("add-review-container");

    if (toggleCheckbox.checked) {
        descriptionContent.classList.add("hidden");
        reviewForm.classList.remove("hidden");
    } else {
        descriptionContent.classList.remove("hidden");
        reviewForm.classList.add("hidden");

    }
}

function showDescription(checkboxId) {
    const toggleCheckbox = document.getElementById(checkboxId);
    toggleCheckbox.checked = !toggleCheckbox.checked;
}

function showEditReview() {
    const reviewContent = document.getElementById("book-review");
    const reviewForm = document.getElementById("edit-review-container");

    reviewForm.classList.remove("hidden");
    reviewContent.classList.add("hidden");
}

function adjustTextareaHeight() {
    var reviewTextarea = document.getElementById("review-input");

    function autoGrowTextarea() {
        reviewTextarea.style.height = "auto";
        reviewTextarea.style.height = (reviewTextarea.scrollHeight + 20) + "px";
    }

    autoGrowTextarea();
}

function toggleConfirmation() {
    const confirmationButtons = document.getElementById("confirmationButtons");
    confirmationButtons.classList.remove("hidden");
    confirmationButtons.classList.add("inline");
}

function hideConfirmation() {
    const confirmationButtons = document.getElementById("confirmationButtons");
    confirmationButtons.classList.add("hidden");
    confirmationButtons.classList.remove("inline");
}

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('global-cover-slider');

    // Function to resize the image
    function resizeImage(image, width) {
        const height = width * 1.5;
        image.style.width = width + 'px';
        image.style.height = height + 'px';
    }

    slider.addEventListener('input', function() {
        const newWidth = this.value;

        const bookCoverImages = document.querySelectorAll('.book-cover-image');
        bookCoverImages.forEach(bookCoverImage => {
            resizeImage(bookCoverImage, newWidth);
        });
    });

    document.body.addEventListener('load', function(event) {
        const target = event.target;
        if (target.classList.contains('book-cover-image')) {
            const newWidth = slider.value;
            resizeImage(target, newWidth);
        }
    }, true); // Use capture phase to ensure the event is captured when it bubbles up

});

document.addEventListener('keyup', function(event) {
    if (event.key === "Escape") {
        closeOverlay();
    }
});

function toggleSidebarView() {
    const genresDiv = document.getElementById('genres-div');
    const genresSearch = document.getElementById('genre-search-container');
    const tagsDiv = document.getElementById('tags-div');
    const isChecked = document.getElementById('toggle-view').checked;

    if (isChecked) {
        genresDiv.style.display = 'none';
        genresSearch.style.display = 'none';
        tagsDiv.style.display = 'block';
    } else {
        genresDiv.style.display = 'block';
        genresSearch.style.display = 'block';
        tagsDiv.style.display = 'none';
    }
}

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "overlay") {
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
    }
});

function filterGenres() {
    const searchTerm = document.getElementById('genre-search').value.toLowerCase();
    const genreLinks = document.querySelectorAll('.genre-link');

    genreLinks.forEach(genre => {
        const tagText = genre.textContent.toLowerCase();
        const shouldShow = tagText.includes(searchTerm);
        genre.style.display = shouldShow ? 'inline' : 'none';
        if (genre.nextElementSibling?.tagName === 'BR') {
            genre.nextElementSibling.style.display = shouldShow ? 'inline' : 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('genre-search').addEventListener('input', filterGenres);
});