var lastTimeID = 0;

$(document).ready(function(){
  activateFirebase();
  window.addEventListener('load', function(){
    initApp()
  });
});

function activateFirebase(){
  // Initialize Firebase
  var config = {
    apiKey: "your key",
    authDomain: "your-id.firebaseapp.com",
    databaseURL: "https://your-id.firebaseio.com/ ",
    storageBucket: "gs://your-id.appspot.com",
    messagingSenderId: "sender id",
  };
  firebase.initializeApp(config);

  var uiConfig = {
    //signInSuccessUrl: 'instructions/',
    signInOptions: [
        // Leave the lines as is for the providers you want to offer your users.
        
        //Fix webview problem of Google authorization!!!
        //firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        firebase.auth.FacebookAuthProvider.PROVIDER_ID,
        firebase.auth.TwitterAuthProvider.PROVIDER_ID,
        {
            provider: firebase.auth.EmailAuthProvider.PROVIDER_ID,
            requireDisplayName: true
        }
        //firebase.auth.EmailAuthProvider.PROVIDER_ID
        ],
    // Terms of service url.
    tosUrl: 'privacy/'
    };
  
  var ui = new firebaseui.auth.AuthUI(firebase.auth());
  ui.start('#firebaseui-auth-container', uiConfig);
}

function initApp(){
  firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    sendToDjango(user);
}
});
}

function sendToDjango(user){
    var displayName = user.displayName;
    var email = user.email;
    var uid = user.uid;
    var providerData = user.providerData;
    var isTouchDevice = function() {  return 'ontouchstart' in window || 'onmsgesturechange' in window; };
    var isDesktop = window.screenX != 0 && !isTouchDevice() ? true : false;
    
    if (!isDesktop){
      var deviceID = android.getDeviceID();
    }
    else {
      var deviceID = 0;
    }
     
  $.ajax({
      url: '/game/register/',
      type: 'POST',
      data: {data: JSON.stringify({
        displayName: displayName,
        email: email,
        uid: uid,
        providerData: providerData,
        deviceID: deviceID
      })},

      success: function( disabled ){
        console.log(disabled);
        if (disabled == "True"){
            window.location.replace("/game/disabled/") 
        }
        if (disabled == "False"){
          window.location.replace("/game/instructions/")
        }
        else{
          window.location.replace("/game/start/")
        }
      }
    });
}


$(function() {
    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
