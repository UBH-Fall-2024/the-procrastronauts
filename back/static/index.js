const socket = io();

let locationText = document.getElementById("location");
let locateButton = document.getElementById("locateButton");
let messageInput = document.getElementById("messageInput");
let messageButton = document.getElementById("messageButton");
let messages = document.getElementById("messages");

locateButton.onclick = () => {locate();}
messageButton.onclick = () => {sendMessage();}

let longitude;
let latitude;

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
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    
    locationText.textContent = "Location: "+latitude.toString()+", "+longitude.toString();
}

function locationError(){
    locationText.textContent = "Location: error";
}

function sendMessage(){

    let message = {
        "id":socket.id,
        "lon": longitude,
        "lat": latitude,
        "msg":cleanMessage(messageInput.value)
    };

    socket.emit("send",JSON.stringify(message));
    console.log("hi");
    messageInput.value = "";
}

function receiveMessage(message){

    message = JSON.parse(message);

    messages.innerText = messages.innerText+"\n"+message["msg"];
}

function cleanMessage(messageText){
    return messageText;
}