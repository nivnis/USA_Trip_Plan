// livesearch for start city
let startCitiesUl = document.getElementById('startCities');
$(document).ready(function(){
    $("#sourceCountry").on("input",function(e){                      
        $("#startCities").empty();
        if ($("#sourceCountry").val() !== "") {
          $.ajax({
            method:"post",
            url:"/livesearch",
            data:{text:$("#sourceCountry").val()},
            success:function(res){  
                $.each(res,function(index,value){
                  let listElement = document.createElement('li')
                  listElement.innerText = value.name + ', ' + value.state ;
                  listElement.addEventListener('click', () => {
                      chooseStartCity(value.name);
                  }, false);
                  startCitiesUl.appendChild(listElement)
                });                                                                                                     
            }
          });
        }                         
    });
});

$(document).ready(function() {
    $("#sourceCountry").on("input",function(e){
      if ($("#sourceCountry").val() == "") {
        $("#startCities").empty();
      }
    });
});

function chooseStartCity(city) {
  $("#sourceCountry").val(city)
  $("#startCities").empty();
}


// livesearch for destination city
let destCitiesUl = document.getElementById('destinationCities');
$(document).ready(function(){
    $("#destinationCountry").on("input",function(e){                      
        $("#destinationCities").empty();
        if ($("#destinationCountry").val() !== "") {
            $.ajax({
            method:"post",
            url:"/livesearch",
            data:{text:$("#destinationCountry").val()},
            success:function(res){  
                $.each(res,function(index,value){
                    let listElement = document.createElement('li')
                    listElement.innerText = value.name + ', ' + value.state;
                    listElement.addEventListener('click', () => {
                        chooseDestinationCity(value.name);
                    }, false);
                    destCitiesUl.appendChild(listElement)
                });                                                                                                     
            }
            });
        }                         
    });
});

$(document).ready(function() {
    $("#destinationCountry").on("input",function(e) {
        if ($("#destinationCountry").val() == "") {
        $("#destinationCities").empty();
        }
    });
});

function chooseDestinationCity(city) {
    $("#destinationCountry").val(city)
    $("#destinationCities").empty();
}


function processCities(result) {
    if ($.isEmptyObject(result)) {
        return
    }
    let startCity = result[0][0]
    let destCity = result[1][0]
    return [startCity, destCity]
}

// sends the filters to server
function sendFilters() {
    parks = document.getElementById("parksCheckbox");
    campsites = document.getElementById("campsCheckbox");
    airbnb = document.getElementById("airbnbCheckbox");
    const list = []
    if (parks.checked) 
        list.push("parks")

    if (campsites.checked) 
        list.push("campsites")

    if (airbnb.checked) 
        list.push("airbnb")
    
    $.ajax({
        type: "POST",
        contentType: 'application/json;charset=UTF-8',
        url: "http://127.0.0.1:5000/locations",
        data: JSON.stringify({filterList: list}),
        success: function(result) {
            for (i = 0; i < 100; i++) {
                addLocationToMap(result[i])
            } 
        },
        error: function(result) {
            alert('error at filters');
        },
        dataType: "json",
    });                              
}
    
// plan trip button click event
$("#plantrip").click(function(e) {
e.preventDefault();
const sourceCity = $("#sourceCountry").val()
const destCity = $("#destinationCountry").val()
$.ajax({
    type: "POST",
    contentType: 'application/json;charset=UTF-8',
    url: "http://127.0.0.1:5000/cities/start_cities",
    data: JSON.stringify({cities: [sourceCity, destCity]}),
    success: function(result) {
        const cities = processCities(result)
        addCityToMap(cities[0])
        addCityToMap(cities[1])
        InitializeCitiesList()
        sendFilters()
    },
    error: function() {
        alert("City not found")
        // location.reload()
        window.location.href = "/"
    },
    dataType: "json",
    });
});

function hideSearch() {
    $('#trip-locations').hide();
    $('#locations').show();
}


$("#saveTrip").click(function(e) {
e.preventDefault();  
const username = localStorage.getItem("userName")
const locations = getTripList()
$.ajax({
    type: "POST",
    contentType: 'application/json;charset=UTF-8',
    url: "http://127.0.0.1:5000/trips/trip_id",
    data: JSON.stringify(
        {
            username: username,
            locations: locations
        }),
    success: function(result) {
        alert("Trip saved Successfully")
        console.log(result)
    },
    error: function() {
        alert('error: unable to submit');
    },
});
});        
