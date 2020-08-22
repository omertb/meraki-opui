// Empty JS for your own code to be here

$('#signInButton').click(function() {
  $('#signInButton').html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true">' +
      '</span>Loading...').addClass('disabled');
});

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
var $deviceTable = $('#deviceTable');
$deviceTable.hide();
var JSON_Selected = $table.bootstrapTable('getSelections');
$(function() {
    $table.on('check.bs.table', function (e, row, $element) {
        console.log('CHECKED');
        checkUnCheckResult();
    });
});
$(function() {
    $table.on('uncheck.bs.table', function (e, row, $element) {
        console.log('UNCHECKED');
        checkUnCheckResult();
    });
});

function checkUnCheckResult() {
    $deviceTable = $('#deviceTable');
    JSON_Selected = $table.bootstrapTable('getSelections');
    if (JSON_Selected.length==0) {
        $deviceTable.fadeOut();
        $deviceTable.bootstrapTable("destroy");
        return
    }
    // console.log(JSON_Selected);
    $.ajax({
        url: "device.json",
        data: JSON.stringify(JSON_Selected),
        type: 'POST',
        contentType: "application/json",
        success: function(data) {
            console.log(data);
            $deviceTable.bootstrapTable("destroy");
            $deviceTable.bootstrapTable({data: data}); // device table source
            $deviceTable.hide();
            $deviceTable.fadeIn();
        },
        error: function(error) {
            console.log(error);
        }
    });
    // $.post("/device.json", JSON_Selected);

}