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
            if(optionValue=='appliance'){
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
        url: "/operator/device.json",
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
        url: "/operator/delete_networks",
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
        url: "/operator/delete_devices",
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
var group_select = document.getElementById("groupSelectMultiple")

$(document).on("click", "#createGroupButton", function(event){
    var new_group_name = $('#newGroupInput').val();
    event.preventDefault();
    $.ajax({
        url: "/groups",
        type: "POST",
        data: new_group_name,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        cache: false,
        processData: false,
        success: function(data) {
            if(data === "Exists!") {
                var output = "Group already exists!";
                newGroupErrorDiv.innerHTML = output;
            }else{
                newGroupErrorDiv.innerHTML = "";
                manageGroupResult.innerHTML = "";
                $groupsTable.bootstrapTable('refresh');
                updateGroupSelect(data);
            }
        }
    });
});

function updateGroupSelect(data){
    var optionHTML = '';
    for (let grp of data) {
        optionHTML += '<option value="' + grp[0].toString() + '">' + grp[1].toString() + '</option>';
    }
    group_select.removeAttribute("data-live-search");
    group_select.classList.remove("selectpicker");
    group_select.innerHTML = optionHTML;
    $('#groupSelectMultiple').addClass('selectpicker');
    $('#groupSelectMultiple').attr('data-live-search', 'true');
    $('#groupSelectMultiple').selectpicker('refresh');
}

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
            var output = '<br>';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            manageGroupResult.innerHTML = output;
            $.get("/groups/groups_select", function(data, status){
                updateGroupSelect(data);
            });
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
            if(Array.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    output += "<li>" + data[i] + "</li>";
                }
            }else{
                output = data;
            }
            $('#groupSelectMultiple').val('default');
            $('#userSelectMultiple').val('default');
            $('#groupSelectMultiple').selectpicker('refresh');
            $('#userSelectMultiple').selectpicker('refresh');
            manageGroupResult.innerHTML = output;
        }
    });
});
var manageNetworkResult = document.getElementById("manageNetworkResult");
$(document).on("click", "#tagGroupButton", function(event){
    event.preventDefault();
    let group_select = $('#groupSelectMultiple2').val();
    let tag_select = $('#tagSelectMultiple').val();
    let group_tag_select = [];
    group_tag_select.push(group_select, tag_select);
        $.ajax({
            url: "/networks/tag_group",
            type: "POST",
            data: JSON.stringify(group_tag_select),
            dataType: "json",
            contentType: "application/json",
            success: function (data) {
                var output = '<br>';
                if (Array.isArray(data)) {
                    for (var i = 0; i < data.length; i++) {
                        output += "<li>" + data[i] + "</li>";
                    }
                } else {
                    output = data;
                }
                $('#groupSelectMultiple2').val('default');
                $('#tagSelectMultiple').val('default');
                $('#groupSelectMultiple2').selectpicker('refresh');
                $('#tagSelectMultiple').selectpicker('refresh');
                manageNetworkResult.innerHTML = output;
            }
        });
});

var networksResultInToolbar = document.getElementById("networksResultInToolbar")
var $networksTable = $('#adminNetworksTable')
$(document).on("click", "#updateNetworksTableButton", function(event){
    $.get("/networks/update_table", function(data, status){
        if(data==="success"){
            $networksTable.bootstrapTable('refresh');
        }else{
            networksResultInToolbar.innerHTML = data;
        }
  });
});

var devicesResultInToolbar = document.getElementById("devicesResultInToolbar")
var $adminDevicesTable = $('#adminDevicesTable')
$(document).on("click", "#updateAdminDevicesTableButton", function(event){
    $.get("/devices/update_table", function(data, status){
        if(data==="success"){
            $adminDevicesTable.bootstrapTable('refresh');
        }else{
            devicesResultInToolbar.innerHTML = data;
        }
  });
});
var $usersTable = $('#usersTable')
// user operator button
$(document).on("click", "#userOperatorButton", function(event){
    JSON_Selected = $usersTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/users/user_operator",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $usersTable.bootstrapTable('refresh');
        }
    });
});

$(document).on("click", "#userAdminButton", function(event){
    JSON_Selected = $usersTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/users/user_admin",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $usersTable.bootstrapTable('refresh');
        }
    });
});

// wait animation with wait-modal
$body = $("body");
$(document).on({
    ajaxStart: function() { $body.addClass("loading");    },
     ajaxStop: function() { $body.removeClass("loading"); }
});