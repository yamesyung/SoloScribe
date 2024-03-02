console.log(emptyLoc);
console.log(locations_json);


var map = L.map('map').setView([20, 20], 2);

var Esri_WorldGrayCanvas = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Esri, TomTom, Garmin, FAO, NOAA, USGS',
	maxZoom: 16,

}).addTo(map);

var AuthorIcon = L.icon({
    iconUrl: authorMarkerPath,

    iconSize:     [38, 38], // size of the icon
    popupAnchor:  [-3, -36] // point from which the popup should open relative to the iconAnchor
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


let markers = L.markerClusterGroup();


locations.forEach(location => {
   let marker = L.marker([location.latitude, location.longitude], { icon: AuthorIcon });
   marker.bindPopup(location.name + '<br>' + location.location_name);
   markers.addLayer(marker);


});
map.addLayer(markers);