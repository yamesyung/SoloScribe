console.log(emptyLoc);
console.log(locations_json);


var map = L.map('map').setView([20, 20], 2);

var Esri_WorldGrayCanvas = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Esri, TomTom, Garmin, FAO, NOAA, USGS',
    maxZoom: 13,

}).addTo(map);

var AuthorIcon = L.icon({
    iconUrl: authorMarkerPath,

    iconSize: [38, 38], // size of the icon
    popupAnchor: [-3, -36] // point from which the popup should open relative to the iconAnchor
});

var locationsJsonElement = document.getElementById('locations_json');
var locations;

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


let markers = L.markerClusterGroup({

});


locations.forEach(location => {
    let marker = L.marker([location.latitude, location.longitude], { icon: AuthorIcon });
    //marker.bindPopup(location.name + '<br>' + location.location_name);
    marker.location_name = location.location_name;
    markers.addLayer(marker);


});
map.addLayer(markers);

markers.on('click', function (a) {
	const locationTitle = a.layer.location_name;
	const divLabelTitle = document.getElementById('authorsLocation');
    divLabelTitle.textContent = locationTitle;

    fetch(`/books/get-authors-map-data/${a.layer.location_name}/`)
        .then(response => response.json())
        .then(data => {
            const authorsList = document.getElementById('authorsList');
            authorsList.innerHTML = '';

            data.authors.forEach(author => {
            const authorElement = document.createElement('span');
            authorElement.classList.add('author-item');
            authorElement.textContent = author.name;
            authorsList.appendChild(authorElement);
            authorsList.appendChild(document.createElement('br'));
            });
        })
        .catch(error => console.error('Error fetching authors data:', error));
});

markers.on('spiderfied', function (a) {
    const locationTitle = a.markers[0].location_name;

	const divLabelTitle = document.getElementById('authorsLocation');
    divLabelTitle.textContent = locationTitle;

	fetch(`/books/get-authors-map-data/${a.markers[0].location_name}/`)
        .then(response => response.json())
        .then(data => {
            const authorsList = document.getElementById('authorsList');
            authorsList.innerHTML = '';

            data.authors.forEach(author => {
                const authorElement = document.createElement('span');
                authorElement.classList.add('author-item');
                authorElement.textContent = author.name;
                authorsList.appendChild(authorElement);
                authorsList.appendChild(document.createElement('br'));
            });
        })
        .catch(error => console.error('Error fetching authors data:', error));
});


document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    const authorsList = document.getElementById('authorsList');
    authorsList.innerHTML = '';
    const divLabelTitle = document.getElementById('authorsLocation');
    divLabelTitle.textContent = '';
  }
});