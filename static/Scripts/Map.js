// Initialize map.
const mymap = L.map('mapid').setView([38.5, -96], 4.5);
let track = []
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    minZoom: 1,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoicGlrYWNodTIzIiwiYSI6ImNrYTJramNkMDAydWEzZnA5M2l5Zmdnc28ifQ.kw350v1vaUcIs6r6oz8p2g'
}).addTo(mymap);

const cityIcon = L.icon({
    iconUrl: "/static/Pictures/city.png",
    iconSize: [45, 45],
    iconAnchor: [0, 0]
});

const parkIcon = L.icon({
    iconUrl: "/static/Pictures/park.png",
    iconSize: [45, 45],
    iconAnchor: [0, 0]
});

const campIcon = L.icon({
    iconUrl: "/static/Pictures/camp.png",
    iconSize: [45, 45],
    iconAnchor: [0, 0]
});

const airbnbIcon = L.icon({
    iconUrl: "/static/Pictures/airbnb.png",
    iconSize: [45, 45],
    iconAnchor: [0, 0]
});

// Global flags for click event.
let isMarkerClicked = false;
let clickedMarker = null;

function onCityClick(marker, city) {
    marker.openPopup()
    isMarkerClicked = true;
    clickedMarker = marker;
}

function onLocationClick(marker, location, type) {
    let popupContent
    $.ajax({
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        url: "http://127.0.0.1:5000/" + type + "/" + location.location_id,    
        success: function(result) {
            if (type === "parks") {
                popupContent = '<h6>' + result[0].name + ', ' + result[0].state +
                 '</h6><h6>Website: <a target="_blank" href=' +
                  result[0].website + '>Click</a>' 
            }
            else if (type === "campsites") {
                popupContent = '<h6>' + result[0].name + ', ' + result[0].state + '</h6><h6>City: ' +
                result[0].city + '</h6><h6>Phone: ' + result[0].phone
            }  
            else { //airbnb
                popupContent = '<h6>' + location.name + ', ' + location.state + '</h6><h6>City: ' +
                 result[0].city + '</h6><h6>Property: ' + result[0].property_type + '</h6><h6>Rank: ' +  
                 result[0].rank_score + '</h6><h6>Website: <a target="_blank" href=' +
                 result[0].listing_url + '>Click</a>' + '<h6>Price: ' + result[0].price + ' $</h6>'
            }
            popupContent += '<br><button id="' + location.location_id + 'end">Add to trip</button>'
            marker.bindPopup(popupContent)
            marker.openPopup()
            const addButton = document.getElementById(location.location_id + 'end')
            addButton.addEventListener("click", function() { addToTrip(location)});
        },
        error: function(result) {
            alert('error: unable to submit');
        },
        dataType: "json",
      });
    isMarkerClicked = true;
    clickedMarker = marker;
}

function addCityToMap(city) {
    const marker = new L.Marker([city.latitude, city.longitude], { icon: cityIcon });
    const popupContent = '<h6>' + city.name + ', ' + city.state + '</h6>'
    marker.bindPopup(popupContent)
    marker.addEventListener('click', () => {
        onCityClick(marker, city);  
    }, false);
    mymap.addLayer(marker);
    shownLocations.push(city)
    return marker;
}

function getIconFromLocation(location) {
    switch(location.type) {
        case 0:
          return "/static/Pictures/camp.png"
        case 1:
            return "/static/Pictures/park.png"
        case 2:
            return "/static/Pictures/airbnb.png"
        default:
            "/static/Pictures/city.png"
      }
}

function addLocationToMap(location) {
    let icon, type
    if(typeof(location) === "undefined") {
        return
    }
    switch(location.type) {
        case 0:
          type = "campsites" 
          icon = campIcon
          break;
        case 1:
            type = "parks"
            icon = parkIcon
          break;
        case 2:
            type = "airbnb"
            icon = airbnbIcon
        break;
        default:
      }
    const marker = new L.Marker([location.latitude, location.longitude], { icon: icon });

    marker.addEventListener('click', () => {
        onLocationClick(marker, location, type);  
    }, false);
    mymap.addLayer(marker);
    shownLocations.push(location)
    shownMarkers.push(marker)
}

function removeMarkerFromMap(marker) {
    mymap.removeLayer(marker);
}

function generateTrack() {
    const tripList = getTripList()["location"]
    const latlngs = []
    for (i = 0; i < tripList.length; i++) {
        for (j = 0; j < shownLocations.length; j++) {
            if (tripList[i] === shownLocations[j].location_id) {
                latlngs.push([shownLocations[j].latitude, shownLocations[j].longitude])
                break
            }
        }
    }
    if (track.length != 0)
        removeMapLine(track)
    track = mapLine(latlngs)
}

function mapLine(latlngs) {
    const polyline = new L.polyline(latlngs, { color: 'red' });
    mymap.addLayer(polyline);
    return polyline;
}

function removeMapLine(line) {
    mymap.removeLayer(line);
}
