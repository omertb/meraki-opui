// custom js codes

$('#signInButton').click(function() {
  $('#signInButton').html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true">' +
      '</span>Loading...').addClass('disabled');
});
$(document).ready(function(){
    $("#netTypeSelect").change(function(){
        $(this).find("option:selected").each(function(){
            var optionValue = $(this).attr("value");
            if(optionValue=='appliance'){
                $("#copyNetworkFormArea").slideUp();
                $("#templateFormArea").slideDown();
            } else{
                $("#templateFormArea").slideUp();
                $("#copyNetworkFormArea").slideDown();
                updateCopyNetworkSelect(optionValue);
            }
        });
    }).change();
});

// update "Select Network To Copy" dropdown menu in "New Network" page according to selected network type
const netJsonUri = 'network.json';
let net_to_copy_dropdown = document.getElementById("selectNetworkToCopy")
const request = new XMLHttpRequest();

function updateCopyNetworkSelect(network_type){
    var optionHTML = '';
    request.open('GET', netJsonUri, true);
    request.onload = function (){
        if (request.status === 200) {
            const data = JSON.parse(request.responseText);
            for (let i = 0; i < data.length; i++) {
                if (data[i].type == network_type) {
                    optionHTML += '<option value="' + data[i].id + '">' + data[i].name + '</option>';
                }
            }
            net_to_copy_dropdown.removeAttribute("data-live-search");
            net_to_copy_dropdown.classList.remove("selectpicker");
            net_to_copy_dropdown.innerHTML = optionHTML;
            $('#selectNetworkToCopy').addClass('selectpicker');
            $('#selectNetworkToCopy').attr('data-live-search', 'true');
            $('#selectNetworkToCopy').selectpicker('refresh');
        }
    }
    request.onerror = function() {
        console.error('An error occurred fetching the JSON from ' + netJsonUri);
    };
    request.send();
}

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
var deviceFormErrorDiv = document.getElementById("deviceFormErrorDiv")
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
            if(data!=="success") {
                var output = '';
                if (Array.isArray(data)) {
                    for (var i = 0; i < data.length; i++) {
                        output += "<li>" + data[i] + "</li>";
                    }
                } else {
                    output = data;
                }
                deviceFormErrorDiv.innerHTML = output;
            }else {
                deviceTableOnNetworkSelect();
            }
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
                // the line below was needed when group_select was in the same page
                // updateGroupSelect(data);
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

// delete group modal
var manageGroupResult = document.getElementById("manageGroupResult");
var deleteGroupResult = document.getElementById("deleteGroupResult");
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
            deleteGroupResult.innerHTML = output;
            // this block below was needed when group_select was in the same page
            /*$.get("/groups/groups_select", function(data, status){
                updateGroupSelect(data);
            });*/
        }
    });
});
$(document).on("click", "#deleteGroupModalClose", function(event){
    deleteGroupResult.innerHTML = "";
});

// "Reset Group" button on /groups page
var resetGroupResult = document.getElementById("resetGroupResult");
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
            resetGroupResult.innerHTML = output;
        }
    });
});

$(document).on("click", "#resetGroupModalClose", function(event){
    resetGroupResult.innerHTML = "";
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
var adminUserTableResult = document.getElementById("adminUserTableResult")
// user operator button
$(document).on("click", "#userOperatorButton", function(event){
    adminUserTableResult.innerHTML = "";
    JSON_Selected = $usersTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/users/user_operator",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $usersTable.bootstrapTable('refresh');
            if (data !== 'success') {
                var output = "";
                output += data;
                adminUserTableResult.innerHTML = output;
            }
        }
    });
});

$(document).on("click", "#userAdminButton", function(event){
    adminUserTableResult.innerHTML = "";
    JSON_Selected = $usersTable.bootstrapTable('getSelections');
    $.ajax({
        url: "/users/user_admin",
        type: "POST",
        data: JSON.stringify(JSON_Selected),
        dataType: "json",
        contentType: "application/json",
        success: function(data) {
            $usersTable.bootstrapTable('refresh');
            if (data !== 'success') {
                var output = "";
                output += data;
                adminUserTableResult.innerHTML = output;
            }
        }
    });
});

// Reset Membership Button on /users page
var resetMembershipResult = document.getElementById("resetMembershipResult")
$(document).on("click", "#resetMembershipButton", function(event){
    JSON_Selected = $usersTable.bootstrapTable('getSelections');
    if (JSON_Selected.length > 0) {
        $.ajax({
            url: "/users/reset_membership",
            type: "POST",
            data: JSON.stringify(JSON_Selected),
            dataType: "json",
            contentType: "application/json",
            success: function (data) {
                $usersTable.bootstrapTable('refresh');
                var output = '<br>';
                if (Array.isArray(data)) {
                    for (var i = 0; i < data.length; i++) {
                        output += "<li>" + data[i] + "</li>";
                    }
                } else {
                    output = data;
                }
                resetMembershipResult.innerHTML = output;
            }
        });
    }
});

$(document).on("click", "#resetMembershipModalClose", function(event){
    adminUserTableResult.innerHTML = "";
    resetMembershipResult.innerHTML = "";
    // $usersTable.bootstrapTable('refresh');
});

// rename devices modal
var renameDeviceResult = document.getElementById("renameDeviceResult")
$(document).on("click", "#renameSelectedDevsButton", function(event){
    let device_name = $('#devNameInput').val();
    let rename_devices_json = {};
    rename_devices_json.device_list = $deviceTable.bootstrapTable('getSelections');
    if (device_name && rename_devices_json.device_list.length > 0) {
        rename_devices_json.device_name = device_name;
        $.ajax({
            url: "/operator/rename_devices",
            type: "POST",
            data: JSON.stringify(rename_devices_json),
            dataType: "json",
            contentType: "application/json",
            success: function (data) {
                deviceTableOnNetworkSelect();
                var output = "<br>";
                if (Array.isArray(data)) {
                    for (var i = 0; i < data.length; i++) {
                        output += "<li>" + data[i] + "</li>";
                    }
                } else {
                    output = data;
                }
                renameDeviceResult.innerHTML = output;
            }
        });
    }
});

$(document).on("click", "#renameDeviceModalClose", function(event){
    renameDeviceResult.innerHTML = "";
    $('#devNameInput').val("");
    // $usersTable.bootstrapTable('refresh');
});

// reboot devices modal
var rebootDeviceResult = document.getElementById("rebootDeviceResult")
$(document).on("click", "#rebootSelectedDevsButton", function(event){
    let reboot_devices_json = [];
    reboot_devices_json = $deviceTable.bootstrapTable('getSelections');
    if (reboot_devices_json.length > 0) {
        $.ajax({
            url: "/operator/reboot_devices",
            type: "POST",
            data: JSON.stringify(reboot_devices_json),
            dataType: "json",
            contentType: "application/json",
            success: function (data) {
                deviceTableOnNetworkSelect();
                var output = "<br>";
                if (Array.isArray(data)) {
                    for (var i = 0; i < data.length; i++) {
                        output += "<li>" + data[i] + "</li>";
                    }
                } else {
                    output = data;
                }
                rebootDeviceResult.innerHTML = output;
            }
        });
    }
});

$(document).on("click", "#rebootDeviceModalClose", function(event){
    rebootDeviceResult.innerHTML = "";
});

var $adminDevicesTable = $('#adminDevicesTable');
$(document).on("click", "#rebootSelectedAdminDevsButton", function(event){
    let reboot_devices_json = [];
    reboot_devices_json = $adminDevicesTable.bootstrapTable('getSelections');
    if (reboot_devices_json.length > 0) {
        $.ajax({
            url: "/admin/reboot_devices",
            type: "POST",
            data: JSON.stringify(reboot_devices_json),
            dataType: "json",
            contentType: "application/json",
            success: function (data) {
                var output = "<br>";
                if (Array.isArray(data)) {
                    for (var i = 0; i < data.length; i++) {
                        output += "<li>" + data[i] + "</li>";
                    }
                } else {
                    output = data;
                }
                rebootDeviceResult.innerHTML = output;
            }
        });
    }
});

$(document).on("click", "#rebootAdminDevicesModalClose", function(event){
    rebootDeviceResult.innerHTML = "";
});


// Select Source Switch Network on Clone Network page

$(document).ready(function() {
    $("#switchNetSelect").change(function () {
        $(this).find("option:selected").each(function () {
            var optionValue = $(this).attr("value");
            //console.log(optionValue);
            sourceSwitchSelectOnSwitchNetSelect(optionValue);
        });
    }).change();
});

const devJsonUri = 'device.json';
let sourceSwitchSelect = document.getElementById("sourceSwitchSelect");
let newSwitchSelect = document.getElementById("newSwitchSelect");
const request_src = new XMLHttpRequest();
const request_dst = new XMLHttpRequest();

function sourceSwitchSelectOnSwitchNetSelect(network){
    var optionHTML = '';
    request_src.open('POST', devJsonUri, true);
    request_src.setRequestHeader('Content-Type', 'application/json');
    request_src.onload = function (){
        if (request_src.status === 200) {
            const data = JSON.parse(request_src.responseText);
            for (let i = 0; i < data.length; i++) {
                    optionHTML += '<option value="' + data[i].id + '">' + data[i].serial + '</option>';
            }
            sourceSwitchSelect.removeAttribute("data-live-search");
            sourceSwitchSelect.classList.remove("selectpicker");
            sourceSwitchSelect.innerHTML = optionHTML;
            $('#sourceSwitchSelect').addClass('selectpicker');
            $('#sourceSwitchSelect').attr('data-live-search', 'true');
            $('#sourceSwitchSelect').selectpicker('refresh');
        }
    }
    request_src.onerror = function(network) {
        console.error('An error occurred fetching the JSON from ' + devJsonUri);
    };
    request_src.send(JSON.stringify(network));
}

$(document).ready(function() {
    $("#destinationNetSelect").change(function () {
        $(this).find("option:selected").each(function () {
            var optionValue = $(this).attr("value");
            //console.log(optionValue);
            destSwitchSelectOnDestNetSelect(optionValue);
        });
    }).change();
});

// const request = new XMLHttpRequest();

function destSwitchSelectOnDestNetSelect(network){
    var optionHTML = '';
    request_dst.open('POST', devJsonUri, true);
    request_dst.setRequestHeader('Content-Type', 'application/json');
    request_dst.onload = function (){
        if (request_dst.status === 200) {
            const data = JSON.parse(request_dst.responseText);
            for (let i = 0; i < data.length; i++) {
                    optionHTML += '<option value="' + data[i].id + '">' + data[i].serial + '</option>';
            }
            newSwitchSelect.removeAttribute("data-live-search");
            newSwitchSelect.classList.remove("selectpicker");
            newSwitchSelect.innerHTML = optionHTML;
            $('#newSwitchSelect').addClass('selectpicker');
            $('#newSwitchSelect').attr('data-live-search', 'true');
            $('#newSwitchSelect').selectpicker('refresh');
        }
    }
    request_dst.onerror = function(network) {
        console.error('An error occurred fetching the JSON from ' + devJsonUri);
    };
    request_dst.send(JSON.stringify(network));
}

// wait animation with wait-modal
$body = $("body");
$(document).on({
    ajaxStart: function() { $body.addClass("loading");    },
     ajaxStop: function() { $body.removeClass("loading"); }
});