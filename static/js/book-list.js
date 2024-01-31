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
    //function for year filtering - TO DO - filter books with no read date
    function( settings, searchData, index, rowData, counter ) {

      var selectedYear = parseInt($('input:checkbox[name="year-checkbox"]:checked').val(), 10);

        // Assuming that the date is in the format "DD-MM-YYYY"
        var dateParts = searchData[6].split('-');
        var rowYear = parseInt(dateParts[2], 10);

        // If no year is selected, include all rows
        if (isNaN(selectedYear)) {
            return true;
        }

        // Check if the row's year matches the selected year
        if (rowYear === selectedYear) {
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
  // Extract distinct years from the third element of each array
  var distinctYears = [...new Set(data.map(book => book[2]?.split('-')[2]).filter(year => year !== undefined))];
  distinctYears.sort((a, b) => b - a);
  return distinctYears;
}

function getDistinctShelves(data) {
  // Extract distinct years from the third element of each array
  var distinctShelves = [...new Set(data.map(book => book[1]))];

  return distinctShelves;
}

function createYearCheckboxes(years, containerSelector) {
  var container = $(containerSelector);

  // Create checkboxes based on distinct years
  years.forEach(function (year) {
    var checkbox = $('<input type="checkbox" class="year-checkbox" name="year-checkbox" value="' + year + '">');
    var label = $('<label>' + year + '</label>');

    container.append(checkbox);
    container.append(label);
    //container.append('<br>');
  })
  container.append('<input type="checkbox" class="year-checkbox" name="year-checkbox" value=""> <label>No read date</label>')
  }

function createShelfCheckboxes(shelf, containerSelector) {
    var container = $(containerSelector);

    // Create checkboxes based on distinct years
    shelf.forEach(function (shelf) {
    var checkbox = $('<input type="checkbox" class="shelf-checkbox" name="shelf-checkbox" value="' + shelf + '">');
    var label = $('<label>' + shelf + '</label>');

    container.append(checkbox);
    container.append(label);
    //container.append('<br>');
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
