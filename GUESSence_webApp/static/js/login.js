var lastTimeID = 0;

$(document).ready(function(){
  //alert("check")
  sendForm();
});

function sendForm(){
    var isTouchDevice = function() {  return 'ontouchstart' in window || 'onmsgesturechange' in window; };
    var isDesktop = window.screenX != 0 && !isTouchDevice() ? true : false;

    if(!isDesktop){
      
      var id = android.getDeviceID();
      console.log(id);
      document.getElementById("id_deviceID").setAttribute("value", id);
    }
}