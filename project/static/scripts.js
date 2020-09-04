// own js codes

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

// network device form post
var formErrorDiv = document.getElementById("formErrorDiv")
$(document).on("submit", "#networkDeviceForm", function(event){
    event.preventDefault();
    $.ajax({
        url: "/",
        type: "POST",
        data: new FormData(this),
        dataType: "json",
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            if(data != null) {
                var output = '';
                for (var i = 0; i < data.length; i++){
                    output += "<li>" + data[i] + "</li>";
                }
                formErrorDiv.innerHTML = output;
                $table.bootstrapTable('refresh');
            }else{
                formErrorDiv.innerHTML = "";
                $table.bootstrapTable('refresh');
            }
        }

    });
});

//vf lines for fade effect for devices table on select,unselect event on network table
// device table creation

var JSON_Selected = $table.bootstrapTable('getSelections');
$(function() {
    $table.on('check.bs.table', function (e, row, $element) {
        //e.preventDefault();
        checkUnCheckResult();
    });
});
$(function() {
    $table.on('uncheck.bs.table', function (e, row, $element) {
        //e.preventDefault();
        checkUnCheckResult();
    });
});
$(function() {
    $table.on('check-all.bs.table', function (e, row, $element) {
        //e.preventDefault();
        checkUnCheckResult();
    });
});
$(function() {
    $table.on('uncheck-all.bs.table', function (e, row, $element) {
        //e.preventDefault();
        checkUnCheckResult();
    });
});

function checkUnCheckResult() {
    //$deviceTable = $('#deviceTable');
    JSON_Selected = $table.bootstrapTable('getSelections');
    if (JSON_Selected.length==0) {
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
            $deviceTable.bootstrapTable("destroy");
            $deviceTable.bootstrapTable({data: data}); // device table source
        },
        error: function(error) {
            console.log(error);
        }
    });

}

// reset device table on page change event for network table;
$(function() {
    $table.on('page-change.bs.table', function (e, row, $element) {
        $deviceTable.bootstrapTable("destroy");
    });
});

// delete network modal
var deleteNetworkResult = document.getElementById("deleteNetworkResult")
$(document).on("click", "#deleteSelectedNetsButton", function(event){
    JSON_Selected = $table.bootstrapTable('getSelections');
    $.ajax({
        url: "/delete_networks",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $table.bootstrapTable('refresh');
            $deviceTable.bootstrapTable("destroy");
            var output = '';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            deleteNetworkResult.innerHTML = output;
        }
    });
});

// delete device modal
var deleteDeviceResult = document.getElementById("deleteDeviceResult")
$(document).on("click", "#deleteSelectedDevsButton", function(event){
    JSON_Selected = $deviceTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/delete_devices",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $table.bootstrapTable('refresh');
            $deviceTable.bootstrapTable("destroy");
            var output = '';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            deleteDeviceResult.innerHTML = output;
        }
    });
});

$('.my-select').selectpicker();

// new group post
var newGroupErrorDiv = document.getElementById("newGroupErrorDiv")
var $groupsTable = $('#groupsTable')

$(document).on("submit", "#createGroupForm", function(event){
    event.preventDefault();
    $.ajax({
        url: "/groups",
        type: "POST",
        data: new FormData(this),
        dataType: "json",
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            if(data != null) {
                var output = data;
                newGroupErrorDiv.innerHTML = output;
                $groupsTable.bootstrapTable('refresh');
            }else{

                newGroupErrorDiv.innerHTML = "";
                $groupsTable.bootstrapTable('refresh');
            }
        }
    });
});

// delete device modal
var manageGroupResult = document.getElementById("manageGroupResult")
$(document).on("click", "#deleteGroupButton", function(event){
    JSON_Selected = $groupsTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/groups/delete_groups",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $groupsTable.bootstrapTable('refresh');
            var output = '';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            manageGroupResult.innerHTML = output;
        }
    });
});

$(document).on("click", "#resetGroupButton", function(event){
    JSON_Selected = $groupsTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/groups/reset_groups",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $groupsTable.bootstrapTable('refresh');
            var output = '';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            manageGroupResult.innerHTML = output;
        }
    });
});

$(document).on("click", "#membershipButton", function(event){
    event.preventDefault();
    let user_select = $('#userSelectMultiple').val();
    let group_select = $('#groupSelectMultiple').val();
    let user_group_array = [];
    user_group_array.push(user_select, group_select);
        $.ajax({
        url: "/groups/add_user",
        type: "POST",
        data: JSON.stringify(user_group_array),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $groupsTable.bootstrapTable('refresh');
            var output = '';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            manageGroupResult.innerHTML = output;
        }
    });
});
var networksResultInToolbar = document.getElementById("networksResultInToolbar")
var $networksTable = $('#networksTable')
$(document).on("click", "#updateNetworksTableButton", function(event){
    $.get("/networks/update_table", function(data, status){
        if(data==="success"){
            $networksTable.bootstrapTable('refresh');
        }else{
            networksResultInToolbar.innerHTML = data;
        }
  });
});

// wait animation with wait-modal
$body = $("body");
$(document).on({
    ajaxStart: function() { $body.addClass("loading");    },
     ajaxStop: function() { $body.removeClass("loading"); }
});