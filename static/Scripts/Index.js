function InitializeCitiesList() {
    const start = shownLocations[0]
    const end = shownLocations[1]
    const iconElement = '<img src="/static/Pictures/city.png" width="30px" height="30px" style="margin-right:20px;">'
    firstCity = document.createElement('li')
    firstCity.id = start.location_id
    firstCity.innerHTML = iconElement + start.name + ', ' + start.state
    firstCity.className = "sortable"
    tripList.appendChild(firstCity)
    lastCity = document.createElement('li')
    lastCity.id = end.location_id
    lastCity.innerHTML = iconElement + end.name + ', ' + end.state
    lastCity.className = "sortable"
    tripList.appendChild(lastCity)
    generateTrack()
}

function addToTrip(location) {
    const listLen = document.getElementById("sortable").getElementsByTagName("li").length
    const lastCurrentElement = document.getElementById("sortable").getElementsByTagName("li")[listLen - 1]

    const iconUrl = getIconFromLocation(location)
    const iconElement = '<img src="' + iconUrl + '" width="30px" height="30px" style="margin-right:20px;">'
    const newLocation = document.createElement('li')
    newLocation.id = location.location_id
    newLocation.innerHTML = iconElement + location.name + ', ' + location.state + '<span class="listClose">&times;</span>'
    newLocation.className= "sortable"
    
    lastCurrentElement.before(newLocation)

    const span = newLocation.lastElementChild
    span.addEventListener("click", function() {
        this.parentElement.remove(this)
        generateTrack()        
      });
      generateTrack()      
}

function getTripList() {
    const tripList = []
    const domList = document.getElementById("sortable").getElementsByTagName("li")
    for (i=0; i < domList.length; i++) {
        tripList.push(domList[i].id)
    }
    return {location: tripList}
}

