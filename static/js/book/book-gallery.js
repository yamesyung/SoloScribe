
// Function to show the overlay
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

    // Auto-grow textarea function
    function autoGrowTextarea() {
        reviewTextarea.style.height = "auto";
        reviewTextarea.style.height = (reviewTextarea.scrollHeight + 20) + "px";
    }

    // Call the auto-grow function
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

        // Update existing book cover images
        const bookCoverImages = document.querySelectorAll('.book-cover-image');
        bookCoverImages.forEach(bookCoverImage => {
            resizeImage(bookCoverImage, newWidth);
        });
    });

    // Event listener to resize newly loaded images
    document.body.addEventListener('load', function(event) {
        const target = event.target;
        if (target.classList.contains('book-cover-image')) {
            const newWidth = slider.value;
            resizeImage(target, newWidth);
        }
    }, true); // Use capture phase to ensure the event is captured when it bubbles up

});