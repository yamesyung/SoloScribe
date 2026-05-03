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

function closeFeedFilters() {
    document.getElementById('feed-filters-wrapper').style.display = 'none';
    document.getElementById('feed-filters').reset();
}

function displayFeedFilters() {
    document.getElementById("feed-filters-wrapper").style.display = "block";
}

document.addEventListener('keyup', function(event) {
    if (event.key === "Escape") {
        const changelog = document.getElementById('changelog');
        const bookEvents = document.getElementById('book-events');
        const feedUpdates = document.querySelectorAll('.feed-update');

        if (changelog && changelog.style.display !== 'none') {
            closeChangelog();
        } else if (bookEvents && bookEvents.style.display !== 'none') {
            closeBookEvents();
        }
        feedUpdates.forEach(el => {
            el.style.display = 'none';
        });
        const feedFilters = document.getElementById("feed-filters-wrapper");
        if (feedFilters) feedFilters.style.display = "none";
    }
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.expandable').forEach(el => {
        const content = el.querySelector('.expandable-content');
        const btn = el.querySelector('.expand-btn');
        // if content isn't actually clamped, hide the button
        if (content.scrollHeight <= content.clientHeight) {
            btn.style.display = 'none';
        }
    });
});

function toggleExpand(btn) {
    const content = btn.previousElementSibling;
    const isCollapsed = content.classList.contains('collapsed');

    content.classList.toggle('collapsed', !isCollapsed);
    content.classList.toggle('expanded', isCollapsed);
    btn.textContent = isCollapsed ? 'Show less' : 'Show more';
}

document.addEventListener('htmx:afterSwap', () => {
    document.querySelectorAll('.expandable').forEach(el => {
        const content = el.querySelector('.expandable-content');
        const btn = el.querySelector('.expand-btn');
        if (content && btn && content.scrollHeight <= content.clientHeight) {
            btn.style.display = 'none';
        }
    });
});

window.addEventListener("scroll", () => {
    document.getElementById("scroll-top").classList.toggle("visible", window.scrollY > 300);
});
