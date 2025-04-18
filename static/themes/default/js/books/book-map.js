//hide the button if emptyLoc is > 0
console.log(emptyLoc);
console.log(locations_json);

var map = L.map('map').setView([20, 20], 2);

var Esri_WorldGrayCanvas = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Esri, TomTom, Garmin, FAO, NOAA, USGS',
	maxZoom: 13,

}).addTo(map);


var locationsJsonElement = document.getElementById('locations_json');
var locations;

// Parse the JSON content and handle null values
if (locationsJsonElement) {

    try {
        locations = JSON.parse(locationsJsonElement.textContent);
        console.log(locations);

    } catch (error) {
        console.error('Error parsing JSON:', error);
    }
} else {
    console.error('Element with ID "locations_json" not found.');
}

//creating leaflet markers
var BookIcon = L.icon({
    iconUrl: bookMarkerPath,

    iconSize:     [40, 40], // size of the icon
    popupAnchor:  [-3, -36] // point from which the popup should open relative to the iconAnchor
});

var BookIconClear = L.icon({
    iconUrl: bookMarkerClearPath,

    iconSize:     [40, 40], // size of the icon
    popupAnchor:  [-3, -36] // point from which the popup should open relative to the iconAnchor
});


let layerSupport = new L.MarkerClusterGroup.LayerSupport();

// Create individual marker cluster groups for each status
let toReadMarkers = L.markerClusterGroup();
let readMarkers = L.markerClusterGroup();
let marker;

locations.forEach(location => {

    if (location.status === "to-read") {
    marker = L.marker([location.latitude, location.longitude], { icon: BookIconClear });
    //marker.bindPopup(location.location_name + '<br>' + location.title + '<br>' + location.year);
    marker.location_name = location.location_name;
    marker.status = location.status;
    toReadMarkers.addLayer(marker);
   }

   if (location.status === "read") {
    marker = L.marker([location.latitude, location.longitude], { icon: BookIcon });
    //marker.bindPopup(location.location_name + '<br>' + location.title + '<br>' + location.year);
    marker.location_name = location.location_name;
    marker.status = location.status;
    readMarkers.addLayer(marker);
   }

});

layerSupport.checkIn(toReadMarkers);
layerSupport.checkIn(readMarkers);
layerSupport.addTo(map);

map.addLayer(toReadMarkers);
map.addLayer(readMarkers);

const overlays = {
    'read': readMarkers,
    'to-read': toReadMarkers
}

const layerControl = L.control.layers(null, overlays).addTo(map);

layerSupport.on('click', function (a) {
    const locationTitle = a.layer.location_name;
	const divLabelTitle = document.getElementById('booksLocation');
    divLabelTitle.textContent = locationTitle;

    fetch(`/books/get-books-map-data/${locationTitle}/`)
        .then(response => response.json())
        .then(data => {
            const booksList = document.getElementById('booksList');
            booksList.innerHTML = '';

            // Initialize categories
            const categories = {
                'read': [],
                'to-read': []
            };

            // Group books by shelf
            data.books.forEach(book => {
                const shelf = book.shelf || 'to-read'; // Default to 'to-read' if shelf is undefined
                if (categories[shelf]) {
                    categories[shelf].push(book);
                }
            });

            // Display books for each category
            Object.keys(categories).forEach(shelf => {
                if (categories[shelf].length > 0) {
                    // Create a header for the shelf
                    const shelfHeader = document.createElement('h4');
                    shelfHeader.textContent = `Shelf: ${shelf}`;
                    booksList.appendChild(shelfHeader);

                    // Add books under this shelf
                    categories[shelf].forEach(book => {
                        const bookElement = document.createElement('span');
                        bookElement.classList.add('book-item');
                        bookElement.textContent = book.title + (book.publication_year ? ` (${book.publication_year})` : '');
                        booksList.appendChild(bookElement);
                        booksList.appendChild(document.createElement('br'));
                    });

                    // Add a line break between shelves
                    booksList.appendChild(document.createElement('hr'));
                }
            });
        })
        .catch(error => console.error('Error fetching books data:', error));
});

layerSupport.on('spiderfied', function (a) {
    const locationTitle = a.markers[0].location_name
	const divLabelTitle = document.getElementById('booksLocation');
    divLabelTitle.textContent = locationTitle;

    fetch(`/books/get-books-map-data/${locationTitle}/`)
        .then(response => response.json())
        .then(data => {
            const booksList = document.getElementById('booksList');
            booksList.innerHTML = '';

            // Initialize categories
            const categories = {
                'read': [],
                'to-read': []
            };

            // Group books by shelf
            data.books.forEach(book => {
                const shelf = book.shelf || 'to-read'; // Default to 'to-read' if shelf is undefined
                if (categories[shelf]) {
                    categories[shelf].push(book);
                }
            });

            // Display books for each category
            Object.keys(categories).forEach(shelf => {
                if (categories[shelf].length > 0) {
                    // Create a header for the shelf
                    const shelfHeader = document.createElement('h4');
                    shelfHeader.textContent = `Shelf: ${shelf}`;
                    booksList.appendChild(shelfHeader);

                    // Add books under this shelf
                    categories[shelf].forEach(book => {
                        const bookElement = document.createElement('span');
                        bookElement.classList.add('book-item');
                        bookElement.textContent = book.title + (book.publication_year ? ` (${book.publication_year})` : '');
                        booksList.appendChild(bookElement);
                        booksList.appendChild(document.createElement('br'));
                    });

                    booksList.appendChild(document.createElement('hr'));
                }
            });
        })
        .catch(error => console.error('Error fetching books data:', error));
});


document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    const booksList = document.getElementById('booksList');
    booksList.innerHTML = '';
    const divLabelTitle = document.getElementById('booksLocation');
    divLabelTitle.textContent = '';
  }
});