

const table = $('#updates-table').DataTable({
  paging: false,
  searching: true,
});

$.fn.dataTable.ext.search.push(function(settings, searchData, index, rowData, counter) {
    var ratings = $('input:checkbox[name="rating"]:checked').map(function() {
        return this.value;
    }).get();

    if (ratings.length === 0) return true;

    var row = table.row(index).node();
    var rating = $(row).find('td:nth-child(4)').attr('data-order');

    return ratings.indexOf(rating) !== -1;
});

$('input:checkbox').on('change', function () {
    table.draw();
});

document.getElementById('clear-filters').addEventListener('click', function () {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function (checkbox) {
      checkbox.checked = false;
    });
    table.draw();
});
