const socket = io();

let locationText = document.getElementById("location");
let locateButton = document.getElementById("locateButton");
let messageInput = document.getElementById("messageInput");
let messageButton = document.getElementById("messageButton");
let messages = document.getElementById("messages");

let messagePresence = document.getElementById("messagePresence");

locateButton.onclick = () => {}
messageButton.onclick = () => {sendMessage();}

let longitude;
let latitude;

let options = {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0,
  };

function connect(){
    if("geolocation" in navigator){

        navigator.geolocation.watchPosition(locationSuccess,locationError,options);
    
        socket.on("receive", (message) => {
            receiveMessage(message);
        });

        socket.on("nearby", (obj) => {
            count_obj = JSON.parse(obj);
            messagePresence.innerText = "Other users in proximity: "+(count_obj["count"]).toString();
        });
    
        
    }else{
        locationText.textContent = "Location: unavailable";
    }
}

socket.on("connect", () => {connect();})

function locationSuccess(position){

    let prev_lat = latitude;

    latitude = position.coords.latitude;
    longitude = position.coords.longitude;

    let me = {
        "id": socket.id,
        "lon": longitude,
        "lat": latitude,
    };

    if(prev_lat == undefined){
        socket.emit("join",JSON.stringify(me));
    }else{
        socket.emit("status",JSON.stringify(me));
    }

    
    locationText.textContent = latitude.toString()+"\n"+longitude.toString();
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

    createMessage(message["from"],message["msg"]);
}

function cleanMessage(messageText){
    return messageText;
}

function createMessage(id, messageText){
    let msgElement = document.createElement("div");
    msgElement.classList.add("message");

    if(id === socket.id){
        msgElement.classList.add("self-message");
    }

    let bubElement = document.createElement("div");
    bubElement.classList.add("bubble");

    msgElement.appendChild(bubElement);

    let msgTextElement = document.createElement("p");
    msgTextElement.classList.add("message-text");
    msgTextElement.innerText = messageText;

    let msgTimeElement = document.createElement("p");
    msgTimeElement.classList.add("message-time");
    let date = new Date();
    msgTimeElement.innerText = date.toLocaleTimeString();

    bubElement.appendChild(msgTextElement);
    bubElement.appendChild(msgTimeElement);

    messages.appendChild(msgElement);

}