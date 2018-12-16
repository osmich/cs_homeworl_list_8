function perform() {
    var urlParams = new URLSearchParams(window.location.search);
    document.getElementById('accountnumber').value = urlParams.get("orgaccess");   
}

window.onload = perform;