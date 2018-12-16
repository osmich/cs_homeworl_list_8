document.getElementById("sendtransfer").onclick = function() {
    document.getElementById("orgaccess").value = document.getElementById("accountnumber").value;
    document.getElementById("accountnumber").value = "broken";

};
