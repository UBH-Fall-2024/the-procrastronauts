const socket = io();

let locationText = document.getElementById("location");
let locateButton = document.getElementById("locateButton");
let messageInput = document.getElementById("messageInput");
let messages = document.getElementById("messages");

locateButton.onclick = () => {locate();}

let self_location = {
    "lat":0.0,
    "lon":0.0,
}

if("geolocation" in navigator){
    locate();

    socket.on("receive", (message) => {
        receiveMessage(message);
    });
    
}else{
    locationText.textContent = "Location: unavailable";
}

function locate(){
    navigator.geolocation.getCurrentPosition(locationSuccess, locationError);
}

function locationSuccess(position){
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;

    self_location["lat"] = latitude;
    self_location["lon"] = longitude;

    
    locationText.textContent = "Location: "+latitude.toString()+", "+longitude.toString();
}

function locationError(){
    locationText.textContent = "Location: error";
}

function sendMessage(){

    let message = {
        "id":socket.id,
        "loc":location,
        "msg":cleanMessage(messageInput.value)
    };

    socket.emit("send",message);
    messageInput.value = "";
}

function receiveMessage(message){

    messages.innerText = messages.innerText+"\n"+message["msg"];
}

function cleanMessage(messageText){
    return messageText;
}