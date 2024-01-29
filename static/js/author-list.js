console.log("datatable here!")

DataTable.datetime('D-MM-YYYY');

var table = $('#authors-table').DataTable({
    lengthMenu: [ [25, 50, 100, -1], [25, 50, 100, "All"] ],
    pageLength : 25,
    columnDefs: [ {targets: 6,orderable: false} ]
    });
