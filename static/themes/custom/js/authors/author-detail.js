var table = $('#books-table').DataTable({
    searching: false,
    lengthChange: false,
    paging: false,
    info: false,
    order: [[ 1, 'asc']],
    columnDefs: [{ targets: 4, orderable: false }]
});


function expandText() {
    var content = document.getElementById('content');
    var showMoreButton = document.getElementById('showMore');
    var showLessButton = document.getElementById('showLess');

    content.style.whiteSpace = 'normal';
    showMoreButton.style.display = 'none';
    showLessButton.style.display = 'inline';
}

function collapseText() {
    var content = document.getElementById('content');
    var showMoreButton = document.getElementById('showMore');
    var showLessButton = document.getElementById('showLess');

    content.style.whiteSpace = 'nowrap';
    showMoreButton.style.display = 'inline';
    showLessButton.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    const colorThief = new ColorThief();

    document.querySelectorAll('.cover-image').forEach((img, index) => {
        if (img.complete) {

            const color = colorThief.getColor(img);
            const row = document.getElementById(`row-${index + 1}`);
            if (color && row) {
                row.style.background = `linear-gradient(to right, rgba(21, 27, 35, 0), rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7))`;
            }
        } else {
            img.onload = function() {
                const color = colorThief.getColor(img);
                const row = document.getElementById(`row-${index + 1}`);
                if (color && row) {
                row.style.background = `linear-gradient(to right, rgba(21, 27, 35, 0), rgba(${color[0]}, ${color[1]}, ${color[2]}, 0.7))`;
                }
            };
        }
    });
});