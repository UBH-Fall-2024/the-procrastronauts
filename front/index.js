let locationText = document.getElementById("location");



if("geolocation" in navigator){

}else{
    locationText.textContent = "unavailable";
}

function locate(){
    
}

function locationSuccess(position){
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    
}