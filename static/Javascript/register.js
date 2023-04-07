function registerButtonClick() {
    $.ajax({
        type: "POST",
        url: "/register",
        data: {
            'username': document.getElementById("username").value,
            'password': document.getElementById("password").value,
            'email': document.getElementById("email").value
        },
        success: function(data) {
            window.location = data;
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log("[ERROR] " + textStatus + ": " + errorThrown);
        }
    })
}