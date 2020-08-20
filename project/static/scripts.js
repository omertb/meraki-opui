// Empty JS for your own code to be here

$(document).ready(function() {
    $("#selectNewExistingForm").change(function () {
        $(this).find("option:selected").each(function () {
            var optionValue = $(this).attr("value");
            if (optionValue == 'new') {
                $("#newNetForm").slideDown();
                $("#existingNetForm").slideUp();
            } else {
                $("#newNetForm").slideUp();
                $("#existingNetForm").slideDown();
            }
        });
    }).change();
});

$(document).ready(function(){
    $("#netTypeSelect").change(function(){
        $(this).find("option:selected").each(function(){
            var optionValue = $(this).attr("value");
            if(optionValue=='firewall'){
                $("#templateFormArea").slideDown();
            } else{
                $("#templateFormArea").slideUp();
                }
            });
        }).change();
});


var $table = $('#networksTable');

$(function() {
    $table.on('check.bs.table', function (e, row, $element) {
        checkUnCheckResult()
    });
});
$(function() {
    $table.on('uncheck.bs.table', function (e, row, $element) {
        checkUnCheckResult()
    });
});

function checkUnCheckResult() {
    var JSON_Selected = $table.bootstrapTable('getSelections');
    console.log(JSON_Selected);
    $.ajax({
        url: "device.json",
        data: JSON.stringify(JSON_Selected),
        type: 'POST',
        dataType: 'json',
        success: function(data) {
            console.log('success');
            // window.location.href = data; // navigate to the new URL
        },
        error: function(error) {
            console.log(error);
        }
    });
    // $.post("/device.json", JSON_Selected);

}