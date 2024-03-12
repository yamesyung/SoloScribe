var table = $('#books-table').DataTable({
    searching: false,
    lengthChange: false,
    paging: false,
    info: false,
    order: [[ 1, 'asc']],
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