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