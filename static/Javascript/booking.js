let map;
let CPH;
let CPH2;
let geocoder;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 6,
  });
  geocoder = new google.maps.Geocoder();

  /* making the departure point */
  geocoder.geocode({
    'address': document.getElementById("mapDeparturePoint").value + " airport"
  }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
        CPH = results[0].geometry.location;
        document.getElementById("departureLocation").innerHTML = results[0]['address_components'][0]['short_name'];
        var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location,
            label: "Departure: " +  document.getElementById("mapDeparturePoint").value
        });
        let center = new google.maps.LatLng(results[0].geometry.location);
        map.panTo(center);
        drawLine();
        // Once the geocoder has finished, the timeZone button (checkbox)
        // can be enabled - as the lat/ lng is required for the timeZone api.
        let timeZoneCheckbox = document.getElementById("departureToLocalTimeCheckbox")
        if (timeZoneCheckbox != null) {
            $("#departureToLocalTimeCheckbox").prop('disabled', false);
        }
    } else {
        CPH = '';
        console.log("[ERROR] Geocode failed with status: " + status);
    }
  })

  /* Making the arrival point */
  geocoder.geocode({
    'address': document.getElementById("mapArrivalPoint").value + " airport"
  }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
        CPH2 = results[0].geometry.location;
        document.getElementById("arrivalLocation").innerHTML = results[0]['address_components'][0]['short_name'];
        var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location,
            label: "Arrival: " + document.getElementById("mapArrivalPoint").value
        });
        drawLine();
        let timeZoneCheckbox = document.getElementById("arrivalToLocalTimeCheckbox")
        if (timeZoneCheckbox != null) {
            $("#arrivalToLocalTimeCheckbox").prop('disabled', false);
        }
    } else {
        CPH2 = '';
        console.log("[ERROR] Geocode failed with status: " + status);
    }
  })
}

function drawLine() {
    /* Flight path (as the crow flies) */
    /* I couldn't see anyway to call this after all the
     google api calls had been made (without making the api calls synchronous
     So instead, this is called after each api call and will generate the line if neither
     point is null*/
  if (CPH != null && CPH2 != null){
      flightPath = new google.maps.Polyline({
        path: [CPH, CPH2],
        geodesic: true,
        strokeColor: '#FF0000',
        strokeOpacity: 1.0,
        strokeWeight: 2
      });
      flightPath.setMap(map);
  }
}

window.initMap = initMap;

function bookButtonClicked(flightId, maxNoSeats) {
    // since i'm not posting via a form, checks must be done separately
    let noSeats = document.getElementById("seats").value
    console.log(flightId);
    if (noSeats == null || noSeats < 0 || noSeats > maxNoSeats || noSeats == ''){
        let newHTML = "<Strong>Invalid input, please make sure your input is between 0 and "
        newHTML += maxNoSeats + "</strong>";
        document.getElementById("bookingWarningText").innerHTML = newHTML;
    } else {
        $.ajax({
            method: 'POST',
            url: "/book",
            data: {
                'flight_id': flightId,
                'no_seats_to_book': noSeats
            },
            success: function (data) {
                window.location = data
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log("[ERROR] " + textStatus + ": " + errorThrown);
            }
        })
    }
}

// Using the google timezones api instead of hard coding them,
// this approach provides better extensibility,
// google timezones api only requires a lat and lng - which is got already from geocoder.
// For consistency, all dates/ times in the database are in NZ Auckland time.

// There is so much different between the changeTimeZoneDeparture and changeTimeZoneArrival
// that I thought I should put them into two separate function - even though they are actually doing
// the same thing.
function changeTimeZoneDeparture(element) {
    let dateElement = document.getElementById('departureDate');
    let timeElement = document.getElementById('departureTime');
    if (element.checked) {
        let xhr = new XMLHttpRequest();
        let latLng = CPH.lat() + ", " + CPH.lng();
        let time = new Date(dateElement.innerHTML + " " + timeElement.innerHTML);
        let timeStamp = time.getTime()/1000 + time.getTimezoneOffset() * 60;
        let url = "https://maps.googleapis.com/maps/api/timezone/json?location="+latLng+"&timestamp="+timeStamp+
                    "&key=AIzaSyDRJupEkbEQLeofq7Njrv9al8SA-NrDdSA";
        xhr.open("GET", url);
        xhr.onload = function() {
            if (xhr.status === 200) {
                let response = JSON.parse(xhr.responseText);
                console.log(response);
                let offset = response['dstOffset'] * 1000 + response["rawOffset"] * 1000;
                let newDate = new Date(timeStamp * 1000 + offset);
                document.getElementById("currentDepartureTimeZone").innerHTML = "("+response['timeZoneName']+")";
                // Vanilla JS date objects do not support date to formatted string, so you either have to import another
                // package or do it manually.
                let dateStrings = dateToString(newDate);
                dateElement.innerHTML = dateStrings[0];
                timeElement.innerHTML = dateStrings[1];
            } else {
                console.log("[ERROR] " + xhr.status + ": " + xhr.statusText);
            }
        }
        xhr.send();
    } else {
        document.getElementById("currentDepartureTimeZone").innerHTML = "(NZ Time)";
        dateElement.innerHTML = document.getElementById("originalDepartureDate").value;
        timeElement.innerHTML = document.getElementById("originalDepartureTime").value;
    }
}

function changeTimeZoneArrival(element) {
    let dateElement = document.getElementById('arrivalDate');
    let timeElement = document.getElementById('arrivalTime');
    if (element.checked) {
        let xhr = new XMLHttpRequest();
        let latLng = CPH.lat() + ", " + CPH.lng();
        let time = new Date(dateElement.innerHTML + " " + timeElement.innerHTML);
        let timeStamp = time.getTime()/1000 + time.getTimezoneOffset() * 60;
        let url = "https://maps.googleapis.com/maps/api/timezone/json?location="+latLng+"&timestamp="+timeStamp+
                    "&key=AIzaSyDRJupEkbEQLeofq7Njrv9al8SA-NrDdSA";
        xhr.open("GET", url);
        xhr.onload = function() {
            if (xhr.status === 200) {
                let response = JSON.parse(xhr.responseText);
                console.log(response);
                let offset = response['dstOffset'] * 1000 + response["rawOffset"] * 1000;
                let newDate = new Date(timeStamp * 1000 + offset);
                document.getElementById("currentArrivalTimeZone").innerHTML = "("+response['timeZoneName']+")";
                let dateStrings = dateToString(newDate);
                dateElement.innerHTML = dateStrings[0];
                timeElement.innerHTML = dateStrings[1];
            } else {
                console.log("[ERROR] " + xhr.status + ": " + xhr.statusText);
            }
        }
        xhr.send();
    } else {
        document.getElementById("currentArrivalTimeZone").innerHTML = "(NZ Time)";
        dateElement.innerHTML = document.getElementById("originalArrivalDate").value;
        timeElement.innerHTML = document.getElementById("originalArrivalTime").value;
    }
}

function dateToString(newDate){
    let newYear = newDate.getFullYear();
    let newMonth = newDate.getMonth() + 1; // JS returns 0 - 11 instead of 1 - 12
    // correcting the format
    if (newMonth < 12) {
        newMonth = "0" + newMonth;
    }
    let newDay = newDate.getDate(); // because obviously getDate means day 0 - 31.
    if (newDay < 10) {
        newDay = "0" + newDay;
    }
    let newHour = newDate.getHours();
    if (newHour < 10) {
        newHour = "0" + newHour;
    }
    let newMinutes = newDate.getMinutes();
    if (newMinutes < 10) {
        newMinutes = "0" + newMinutes;
    }
    let newSec = newDate.getSeconds();
    if (newSec < 10) {
        newSec = "0" + newSec;
    }
    return [newYear + "-" + newMonth + "-" + newDay,
            newHour + ":" + newMinutes + ":" + newSec];
}