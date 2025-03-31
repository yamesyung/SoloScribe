console.log("datatable here!")

DataTable.datetime('D-MM-YYYY');

var table = $('#authors-table').DataTable({
    lengthMenu: [[25, 50, 100, -1], [25, 50, 100, "All"]],
    pageLength: 25,
    columnDefs: [{ targets: 7, orderable: false }]
});


$('#authors-table').on('draw.dt', function() {
    const info = $('.dataTables_info');
    info.addClass('animate-info');

    // Remove the class after the animation completes
    setTimeout(() => {
        info.removeClass('animate-info');
    }, 300); // Match the duration with the CSS animation
});