/**
 * [bookButtonClick function to direct user to the booking page for a flight]
 * @param {[int]} flight_id
 * @return {[NONE]}
**/
function bookButtonClick(flight_id) {
    $.ajax({
        method: 'GET',
        url: "/booking",
        data: {
            'flight_id': flight_id
        },
        success: function(data) {
            window.location = data;
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log("[ERROR] " + textStatus + ": " + errorThrown);
        }
    })
}

/**
 * [searchButtonClick function to search all flights]
 * @return {[NONE]}
**/
/* TODO: given the size of the data, its not a problem. But really, all previous ajax requests should be either halted, or waited until complete.
    I've found that since ajax is asynchronous: The first search request might be for 'a', then the second is for 'acd'. 'acd' will complete before
    'a' - which results in incorrect data being displayed. Alternately, block the user from searching until the last search request is completed.
    This is only really a problem for larger databases.
*/
function searchButtonClick() {
    searchTerm = document.getElementById("searchQuery");
    interconnecting = document.getElementById("interconnectingFlightsCheckbox")
    startDate = document.getElementById("startDate");
    endDate = document.getElementById("endDate");
    $.ajax({
        method: 'GET',
        url: "/search_all_flights",
        data: {
            "search_term": searchTerm.value,
            "interconnecting_flights": interconnecting.checked,
            "start_date": startDate.value,
            "end_date": endDate.value
        },
        success: function(data) {
            displayFlightData(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log("[ERROR] " + textStatus + ": " + errorThrown);
        }
    })
}

/**
 * [sort similar to search. Sorts the data by column. Does make another call to the database.
 * Maybe this should change, so the last search query is stored in local storage to reduce the number
 * of calls to the database]
 * @param {[object]} button - The button the user just clicked.
 * @param {[string]} column - The column to sort by.
 * @return {[NONE]}
**/
function sort(button, column) {
    let img = button.parentNode.getElementsByTagName("img")[0];
    let direction;
    let interconnecting = document.getElementById("interconnectingFlightsCheckbox")
    let searchTerm = document.getElementById("searchQuery");
    let startDate = document.getElementById("startDate");
    let endDate = document.getElementById("endDate");
    if (img == null) {
        let lastSortButtonId = sessionStorage.getItem("lastSortButtonId");
        let lastSortButton = document.getElementById(lastSortButtonId);
        if (lastSortButton != null) {
            let parentNodeElement = lastSortButton.parentNode;
            let imgElement = parentNodeElement.getElementsByTagName("img")[0]
            if (imgElement != null){
                parentNodeElement.removeChild(imgElement);
            }
        }
        button.parentNode.innerHTML += '<img src="static/images/sortImage.svg" style="transform: scaleY(-1);" />'
        direction = "ASC";
    } else {
        if (img.style.transform == "scaleY(-1)") {
            direction = "DESC";
            img.style.removeProperty('transform');
        } else {
            direction = "ASC"
            img.style.transform = "scaleY(-1)"
        }
    }
    sessionStorage.setItem("lastSortButtonId", button.id);
    $.ajax({
        method: "GET",
        url: "/search_all_flights",
        data: {
            "search_term": searchTerm.value,
            "start_date": startDate.value,
            "end_date": endDate.value,
            "sort_column": column,
            "sort_direction": direction,
            "interconnecting_flights": interconnecting.checked,
        },
        success: function(data) {
            displayFlightData(data)
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log("[ERROR] " + textStatus + ": " + errorThrown);
        }
    })
}

/**
 * [displayFlightData function to display the flight data]
 * @param {[JSON]} data - an array of flight data
 * @return {[NONE]}
**/
function displayFlightData(data) {
    $('#flightsTable tr:not(:first)').remove();
    newHtml = "";
    for (var i in data) {
        let flight = data[i];
        // The dates need to be converted into the correct format for js.
        // The valid js date formats are "yyyy-mm-dd", "mm/dd/yyyy", "Mar 25 2015"
        let flightDateSplit =  flight[2].split("/")
        let jsDate = flightDateSplit[1] + "/" + flightDateSplit[0] + "/" + flightDateSplit[2];
        let flightDepartureDateTime = new Date(jsDate + " " + flight[3]);
        let dateNow = Date.now();
        if (flightDepartureDateTime < dateNow) {
            newHtml += "<tr class='departed'>";
        } else if (flight[13] == 0) {
            newHtml += "<tr class='booked'>";
        } else {
            newHtml += "<tr class='available'>";
        }
        newHtml += "<td>" + flight[1] + "</td>";
        newHtml += "<td>" + flight[2] + "@" + flight[3] +"</td>";
        newHtml += "<td>" + flight[4] + "</td>";
        newHtml += "<td>" + flight[11] + "</td>";
        if (flight[13] > 0) {
            newHtml += "<td>" + flight[13] + "</td>";
        } else {
            newHtml += "<td><strong>Fully booked</strong></td>";
        }
        newHtml += "<td>$" + flight[8] + "</td>";
        newHtml += "<td><button onclick=\"window.location.href='/booking?flight_id=" + flight[0] +
                   "'\" class='tableButton'>";
        if (flightDepartureDateTime < dateNow) {
            newHtml += "<b>Departed</b>";
        } else if (flight[13] > 0) {
            newHtml += "Book";
        } else {
            newHtml += "View";
        }
        newHtml += "</button></td></tr>";
    }
    document.getElementById("flightsTable").innerHTML += newHtml;
}