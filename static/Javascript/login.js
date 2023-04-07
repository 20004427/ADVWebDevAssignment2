function loginButtonClick() {
    $.ajax({
        method: "POST",
        url: "/login",
        data: {
            'username': document.getElementById("username").value,
            'password': document.getElementById("password").value
        },
        success: function(data) {
            window.location = data
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log("[ERROR] " + textStatus + ": " + errorThrown);
        }
    })
}