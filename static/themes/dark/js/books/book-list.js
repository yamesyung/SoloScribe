console.log(bookData);

DataTable.datetime('D-MM-YYYY');

$(document).ready( function () {

       //function to filter bookshelves
      $.fn.dataTable.ext.search.push(
    function( settings, searchData, index, rowData, counter ) {
      var bookshelves = $('input:checkbox[name="shelf-checkbox"]:checked').map(function() {
        return this.value;
      }).get();

      if (bookshelves.length === 0) {
        return true;
      }

      if (bookshelves.indexOf(searchData[3]) !== -1) {
        return true;
      }

      return false;
    }
  );

//function for rating filtering
  $.fn.dataTable.ext.search.push(
    function( settings, searchData, index, rowData, counter ) {
      var ratings = $('input:checkbox[name="rating"]:checked').map(function() {
        return this.value;
      }).get();

      if (ratings.length === 0) {
        return true;
      }

      if (ratings.indexOf(searchData[2]) !== -1) {
        return true;
      }

      return false;
    }
  );

    $.fn.dataTable.ext.search.push(
    //function for year filtering
    function( settings, searchData, index, rowData, counter ) {

      var selectedYears = $('input:checkbox[name="year-checkbox"]:checked').map(function() {
        return parseInt($(this).val(), 10);
        }).get();

        // Assuming that the date is in the format "DD-MM-YYYY"
        var dateParts = searchData[7].split('-');
        var rowYear = parseInt(dateParts[2], 10);

    if (selectedYears.length === 0) {
        return true;
    }

    // Check if the row's year is in the selected years array
    if (selectedYears.includes(rowYear)) {
        return true;
    }

        return false;
    }
  );

  //function for empty date filtering
  $.fn.dataTable.ext.search.push(
    function( settings, searchData, index, rowData, counter ) {
      var years = $('input:checkbox[name="no-year-checkbox"]:checked').map(function() {
        return this.value;
      }).get();

      if (years.length === 0) {
        return true;
      }

      if (years.indexOf(searchData[7]) !== -1) {
        return true;
      }

      return false;
    }
  );

  // Extract distinct years
var distinctYears = getDistinctYears(bookData);
var distinctShelves = getDistinctShelves(bookData);

// Create checkboxes in HTML
createYearCheckboxes(distinctYears, '#year-checkbox-container');
createShelfCheckboxes(distinctShelves, '#shelf-checkbox-container')

function getDistinctYears(data) {
  // Extract distinct years
  var distinctYears = [...new Set(data.map(book => book[2]?.split('-')[2]).filter(year => year !== undefined))];
  distinctYears.sort((a, b) => b - a);
  return distinctYears;
}

function getDistinctShelves(data) {
  // Extract distinct shelves
  var distinctShelves = [...new Set(data.map(book => book[1]))];

  return distinctShelves;
}

function createYearCheckboxes(years, containerSelector) {
  var container = $(containerSelector);

  // Create checkboxes based on distinct years
  years.forEach(function (year) {
    var checkbox = $('<input type="checkbox" class="year-checkbox" name="year-checkbox" id="year-checkbox-' + year + '" value="' + year + '">');
    var label = $('<label for ="year-checkbox-' + year + '">&nbsp;' + year + '</label>');

    container.append(checkbox);
    container.append(label);
    container.append('<br>');
  })
  container.append('<input type="checkbox" class="year-checkbox" name="no-year-checkbox" value="" id="no-year-checkbox"><label for="no-year-checkbox">&nbsp;No read date</label>')
  }

function createShelfCheckboxes(shelf, containerSelector) {
    var container = $(containerSelector);

    shelf.forEach(function (shelf) {
    var checkbox = $('<input type="checkbox" class="shelf-checkbox" name="shelf-checkbox" id="shelf-checkbox-' + shelf + '" value="' + shelf + '">');
    var label = $('<label for ="shelf-checkbox-' + shelf + '">&nbsp;' + shelf + '</label>');

    container.append(checkbox);
    container.append(label);
    container.append('<br>');
    })
}

var table = $('#books-table').DataTable({
lengthMenu: [ [25, 50, 100, -1], [25, 50, 100, "All"] ],
pageLength : 25,
order: [[ 7, 'desc']],

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

} );

$('#books-table').on('draw.dt', function() {
    const info = $('.dataTables_info');
    info.addClass('animate-info');

    // Remove the class after the animation completes
    setTimeout(() => {
        info.removeClass('animate-info');
    }, 300); // Match the duration with the CSS animation
});