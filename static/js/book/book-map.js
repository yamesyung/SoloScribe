//hide the button if emptyLoc is > 0
console.log(emptyLoc);
console.log(locations);


document.addEventListener('DOMContentLoaded', function () {

    let locationCount = emptyLoc;
    let estTime = emptyLoc * 0.016;

    document.getElementById('locCount').innerText = locationCount;
    document.getElementById('locTimeM').innerText = Math.ceil(estTime);
});