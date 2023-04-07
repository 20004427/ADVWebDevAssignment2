let geocoder;

function initMap() {
    geocoder = new google.maps.Geocoder();
    let elements = document.getElementsByClassName("flightDepartureLocCode");
    for (let e in elements) {
        let code = elements[e].innerHTML;
        let pToInsertTo = elements[e].parentElement;
        geocoder.geocode({
            'address': code + " airport"
        }, function(results, status) {
            if (status === google.maps.GeocoderStatus.OK) {
                console.log(results);
                pToInsertTo.innerHTML = results[0]['address_components'][0]['short_name'];
            }
        })
    }
}

function openCancelOverlay(flightId, maxSeats){
    let cancelBookingOverlay = document.getElementById("cancelBookingOverlay");
    let cancelBookingForm = document.getElementById("cancelBookingForm");
    cancelBookingForm.innerHTML += "<input type='hidden' name='flightId' value='" + flightId + "'"
                                    + " id='cancelBookingFormFlightId'>";
    cancelBookingForm.innerHTML += "<input type='hidden' name='maxSeats' value='" + maxSeats + "'"
                                    + " id='cancelBookingFormMaxSeats'>";
    document.getElementById("seats").setAttribute("max", maxSeats);
    // If they only have one seat booked, then there is no point opening the dialog.
    if (maxSeats == 1) {
        document.getElementById("seats").value = 1;
        submitCancelBooking();
    } else {
        cancelBookingOverlay.style.display = "block";
    }
}

function closeCancelOverlay() {
    let cancelBookingOverlay = document.getElementById("cancelBookingOverlay");
    cancelBookingOverlay.style.display = "none";
}

function submitCancelBooking() {
    let flightId = document.getElementById("cancelBookingFormFlightId");
    let seatsToCancel = document.getElementById("seats");
    let maxSeats = document.getElementById("cancelBookingFormMaxSeats");
    if (! confirm("Are you sure you want to cancel your booking?")) {
        return;
    }
    $.ajax({
        method: "POST",
        url: "/cancel_booking",
        data: {
            "flight_id": flightId.value,
            "seats_to_cancel": seatsToCancel.value,
            "max_seats_to_cancel": maxSeats.value
        },
        success: function(data) {
            window.location = data
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (jqXHR.status == 2) {
                document.getElementById("cancelBookingOverlayWarningText").innerHTML = "Invalid input, "
                                        + "Please try again."
            } else {
                console.log(jqXHR.status);
                console.log("[ERROR] " + textStatus + ": " + errorThrown)
            }
        }
    })
}