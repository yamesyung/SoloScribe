DataTable.datetime('D-MM-YYYY');

var table = $('#authors-table').DataTable({
    lengthMenu: [[15, 30, 60, -1], [15, 30, 60, "All"]],
    pageLength: 30,
    columnDefs: [
        { targets: 7, orderable: false },
        { targets: [1, 2, 6, 7], visible: false }
    ]
});


$('#authors-table').on('draw.dt', function() {
    const info = $('.dataTables_info');
    info.addClass('animate-info');

    setTimeout(() => {
        info.removeClass('animate-info');
    }, 300);
});

$('.dataTables_filter input')
  .off()
  .on('keyup', function () {
      table.columns(0).search(this.value).draw();
});

$('.dataTables_filter input').attr('placeholder', 'Search...');