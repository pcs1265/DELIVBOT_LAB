
const pos_update_checkbox = document.querySelector('#pos_update');

function refresh_pos(){
    var requestURL = window.location.href + 'status/robot';
    var request = new XMLHttpRequest();
    request.open('GET', requestURL);
    request.responseType = 'json';
    request.send();
    request.onload = function() {
        document.getElementById("curr_pos_x").innerText = request.response.pos_x;
        document.getElementById("curr_pos_y").innerText = request.response.pos_y;
        document.getElementById("curr_ori_w").innerText = request.response.ori_w;
        document.getElementById("curr_ori_z").innerText = request.response.ori_z;
        if(request.response.status_code == 1){
            document.getElementById("curr_action_status_code").innerText = request.response.status_code + " (Navigating)";
        }else if(request.response.status_code == 2){
            document.getElementById("curr_action_status_code").innerText = request.response.status_code + " (Canceled)";
        }else if(request.response.status_code == 3){
            document.getElementById("curr_action_status_code").innerText = request.response.status_code + " (Succeeded)";
        }else if(request.response.status_code == 4){
            document.getElementById("curr_action_status_code").innerText = request.response.status_code + " (Aborted)";
        }else{
            document.getElementById("curr_action_status_code").innerText = request.response.status_code + " (Unknown)";
        }
        
        document.getElementById("curr_action_status_text").innerText = request.response.status_text;
    }
    if(pos_update_checkbox.checked){
        setTimeout(refresh_pos, 500)
    }
}

pos_update_checkbox.addEventListener('change', () => {
    if (pos_update_checkbox.checked) {
        refresh_pos()
    }
});

active_goal = false;
const make_goal_button = document.querySelector('#make_goal');
const input_pos_x = document.querySelector('#input_pos_x');
const input_pos_y = document.querySelector('#input_pos_y');
const input_ori_w = document.querySelector('#input_ori_w');
const input_ori_z = document.querySelector('#input_ori_z');
make_goal_button.addEventListener('click', () => {
    if(input_pos_x.value == ""){
        alert("target_x should not be empty.")
        return
    }
    if(input_pos_y.value == ""){
        alert("target_y should not be empty.")
        return
    }
    if(input_ori_w.value == ""){
        input_ori_w.value = "1.0";
    }
    if(input_ori_z.value == ""){
        input_ori_z.value = "0.0";
    }
    var requestURL = window.location.href + 'action';
    var request = new XMLHttpRequest();
    request.open('POST', requestURL);
    request.setRequestHeader("Content-Type", "application/json");
    request.responseType = 'json';
    request.send(
        JSON.stringify({
            pos_x: (Number)(input_pos_x.value),
            pos_y: (Number)(input_pos_y.value),
            ori_w: (Number)(input_ori_w.value),
            ori_z: (Number)(input_ori_z.value)
        })
    );
    document.getElementById("goal_status").innerText = "Goal sent.";
    request.onload = function() {
        if(request.response.result == 3){
            document.getElementById("goal_status").innerText =  "Goal reached. Took " + request.response.elapsed_time + " second(s)";
        }else if(request.response.result == 2){
        }
        else{
            document.getElementById("goal_status").innerText =  "A problem occurred during navigation. Check the status.";
        }
        
    }
});

const cancel_goal_button = document.querySelector('#cancel_goal');
cancel_goal_button.addEventListener('click', () => {
    var requestURL = window.location.href + 'action';
    var request = new XMLHttpRequest();
    request.open('DELETE', requestURL);
    request.send();
});


var cmd_linear_velocity = 0;
var cmd_angular_velocity = 0;

function send_cmd_vel(){
    var requestURL = window.location.href + 'cmd_vel/';
    var request = new XMLHttpRequest();
    request.open('POST', requestURL);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(
        JSON.stringify({
            linear_velocity: cmd_linear_velocity,
            angular_velocity: cmd_angular_velocity
        })
    );
    document.getElementById("curr_linear_vel").innerText = cmd_linear_velocity.toFixed(2);
    document.getElementById("curr_angular_vel").innerText = cmd_angular_velocity.toFixed(2);
    navigator.vibrate(1);
}

const cmd_linear_up = document.querySelector('#cmd_linear_up_button');
cmd_linear_up.addEventListener('click', () => {
    if(cmd_linear_velocity + 0.03 > 0.26){
        return;
    }
    cmd_linear_velocity += 0.03;
    send_cmd_vel();
});
const cmd_linear_down = document.querySelector('#cmd_linear_down_button');
cmd_linear_down.addEventListener('click', () => {
    if(cmd_linear_velocity - 0.03 < -0.26){
        return;
    }
    cmd_linear_velocity -= 0.03;
    send_cmd_vel();
});
const cmd_angular_up = document.querySelector('#cmd_angular_up_button');
cmd_angular_up.addEventListener('click', () => {
    if(cmd_angular_velocity + 0.2 > 1.8){
        return;
    }
    cmd_angular_velocity += 0.2;
    send_cmd_vel();
});
const cmd_angular_down = document.querySelector('#cmd_angular_down_button');
cmd_angular_down.addEventListener('click', () => {
    if(cmd_angular_velocity - 0.2 < -1.8){
        return;
    }
    cmd_angular_velocity -= 0.2;
    send_cmd_vel();
});
const cmd_stop = document.querySelector('#cmd_stop_button');
cmd_stop.addEventListener('click', () => {
    cmd_linear_velocity = 0;
    cmd_angular_velocity = 0;
    send_cmd_vel();
});



const checkDB_button = document.querySelector('#checkDB');
checkDB_button.addEventListener('click', () => {
    var requestURL = window.location.href + 'op/checkDB';
    var request = new XMLHttpRequest();
    request.open('POST', requestURL);
    request.send();
});

const postUserOccu_button = document.querySelector('#POSTuserOccu');
postUserOccu_button.addEventListener('click', () => {
    var requestURL = window.location.href + 'op/userOccupation';
    var request = new XMLHttpRequest();
    request.open('POST', requestURL);
    request.send();
});

const deleteUserOccu_button = document.querySelector('#DELETEuserOccu');
deleteUserOccu_button.addEventListener('click', () => {
    var requestURL = window.location.href + 'op/userOccupation';
    var request = new XMLHttpRequest();
    request.open('DELETE', requestURL);
    request.send();
});

