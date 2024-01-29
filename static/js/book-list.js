DataTable.datetime('D-MM-YYYY');

var table = $('#books-table').DataTable({
    lengthMenu: [ [25, 50, 100, -1], [25, 50, 100, "All"] ],
    pageLength : 25,
    order: [[ 7, 'desc']],

});
