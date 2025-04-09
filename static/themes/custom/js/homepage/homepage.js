document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("calendar-toggle");


    toggleButton.addEventListener("click", function () {
        const bookEvents = document.getElementById("book-events");
        const calendar = document.getElementById("calendar");
        calendar.classList.toggle("hidden");

        if (bookEvents) {
            bookEvents.classList.toggle("hidden");
        }
    });
});


function closeChangelog() {
    document.getElementById('changelog').style.display = 'none';
}

function closeBookEvents() {
    document.getElementById('book-events').style.display = 'none';
}

document.addEventListener('keyup', function(event) {
    if (event.key === "Escape") {
        const changelog = document.getElementById('changelog');
        const bookEvents = document.getElementById('book-events');

        if (changelog && changelog.style.display !== 'none') {
            closeChangelog();
        } else if (bookEvents && bookEvents.style.display !== 'none') {
            closeBookEvents();
        }
    }
});
