
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

    if (toggleCheckbox.checked) {
        descriptionContent.classList.add("hidden");
        reviewContent.classList.remove("hidden");
    } else {
        descriptionContent.classList.remove("hidden");
        reviewContent.classList.add("hidden");

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