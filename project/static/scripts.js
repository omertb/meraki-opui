// own js codes

$('#signInButton').click(function() {
  $('#signInButton').html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true">' +
      '</span>Loading...').addClass('disabled');
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
        url: "/operator/new_network",
        type: "POST",
        data: new FormData(this),
        dataType: "json",
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            if(data != null) {
                var output = '<br>';
                if(Array.isArray(data)) {
                    for (var i = 0; i < data.length; i++) {
                        output += "<li>" + data[i] + "</li>";
                    }
                    formErrorDiv.innerHTML = output;
                }else{
                    formErrorDiv.innerHTML = output + data;
                }
                $table.bootstrapTable('refresh');
            }else{
                formErrorDiv.innerHTML = "";
                $table.bootstrapTable('refresh');
            }
        }

    });
});

$(function() {
    $("#existingNetSelect").on("change", function () {
        //e.preventDefault();
        deviceTableOnNetworkSelect();
        $("#devicesTextArea").val('');
    });
});
function deviceTableOnNetworkSelect() {
    //$deviceTable = $('#deviceTable');
    var selectedNetwork = $("#existingNetSelect").val();
    if (selectedNetwork.length==0) {
        $deviceTable.bootstrapTable("destroy");
        return
    }
    // console.log(JSON_Selected);
    $.ajax({
        url: "/operator/device.json",
        data: JSON.stringify(selectedNetwork),
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

$(document).on("click", "#addDeviceFormButton", function(event){
    event.preventDefault();
    let network_select = $("#existingNetSelect").val();
    let devices = $("#devicesTextArea").val();
    let network_device_dict = JSON.stringify({network:network_select, devices:devices});
        $.ajax({
        url: "/operator/add_devices",
        type: "POST",
        data: network_device_dict,
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            var output = '';
            if(Array.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    output += "<li>" + data[i] + "</li>";
                }
            }else{
                output = data;
            }
            deviceTableOnNetworkSelect();
            $('#formErrorDiv').innerHTML = output;
            // $('#existingNetSelect').val('default');
            // $('#existingNetSelect').selectpicker('refresh');
        }
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
            var output = '<br>';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            deleteNetworkResult.innerHTML = output;
        }
    });
});

// commit network modal
var commitNetworkResult = document.getElementById("commitNetworkResult")
$(document).on("click", "#commitSelectedNetsButton", function(event){
    JSON_Selected = $table.bootstrapTable('getSelections');
    $.ajax({
        url: "/operator/commit_networks",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $table.bootstrapTable('refresh');
            var output = '<br>';
            if(Array.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    output += "<li>" + data[i] + "</li>";
                }
            }else {
                output += data;
            }
            commitNetworkResult.innerHTML = output;
        }
    });
});

$(document).on("click", "#commitNetworkModalClose", function(event){
    commitNetworkResult.innerHTML = "";
});
$(document).on("click", "#deleteNetworkModalClose", function(event){
    deleteNetworkResult.innerHTML = "";
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
            var output = '<br>';
            for (var i = 0; i < data.length; i++){
                output += "<li>" + data[i] + "</li>";
            }
            deleteDeviceResult.innerHTML = output;
        }
    });
});

$(document).on("click", "#deleteDevicesModalClose", function(event){
    deleteDeviceResult.innerHTML = "";
    deviceTableOnNetworkSelect();
});

// commit device modal
var commitDeviceResult = document.getElementById("commitDeviceResult")
$(document).on("click", "#commitSelectedDevsButton", function(event){
    JSON_Selected = $deviceTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/operator/commit_devices",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            var output = '<br>';
            if(Array.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    output += "<li>" + data[i] + "</li>";
                }
            }else {
                output += data;
            }
            commitDeviceResult.innerHTML = output;
        }
    });
});

$(document).on("click", "#commitDeviceModalClose", function(event){
    commitDeviceResult.innerHTML = "";
    deviceTableOnNetworkSelect();
});


$('.my-select').selectpicker();

// new group
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
            var output = '<br>';
            if(Array.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    output += "<li>" + data[i] + "</li>";
                }
            }else{
                output += data;
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