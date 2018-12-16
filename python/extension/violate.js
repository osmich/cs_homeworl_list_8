document.getElementById("sendtransfer").onclick = function() {
    document.getElementById("orgaccess").value = document.getElementById("accountnumber").value;
    document.getElementById("accountnumber").value = "broken";

};

// window.some_variable = <?php $_POST['accountnumber']; ?>;
// console.log(window.some_variable)


// $('#myForm').submit(function(e){
//     e.preventDefault();
//     $.ajax({
//         url: $("#myForm").attr("action"),
//         data: $("#myForm :input").serializeArray(),
//         type: 'post',
//         dataType: 'html',
//         success: function(data){
//             $("#result").html(data);
//         },
//         beforeSend: function(){
//             $("#loading").show()
//         },
//         complete: function(data){
//             $("#loading").hide()
//         }
//     });
// });