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
    bubElement.style.backgroundColor = "#"+(string_to_color(id,50))+"10";

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

    msgElement.scrollIntoView({ behavior: "smooth", block: "end", inline: "nearest" });
}

// from https://github.com/brandoncorbin/string_to_color
function string_to_color(a,b){"use strict";var b="number"==typeof b?b:-10,c=function(a){for(var b=0,c=0;c<a.length;c++)b=a.charCodeAt(c)+((b<<5)-b);return b},d=function(a,b){var c=parseInt(a,16),d=Math.round(2.55*b),e=(c>>16)+d,f=(255&c>>8)+d,g=(255&c)+d;return(16777216+65536*(255>e?1>e?0:e:255)+256*(255>f?1>f?0:f:255)+(255>g?1>g?0:g:255)).toString(16).slice(1)},e=function(a){var b=(255&a>>24).toString(16)+(255&a>>16).toString(16)+(255&a>>8).toString(16)+(255&a).toString(16);return b};return d(e(c(a)),b)}