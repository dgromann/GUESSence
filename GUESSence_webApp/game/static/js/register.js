var lastTimeID = 0;

$(document).ready(function(){
  activateFirebase();
  window.addEventListener('load', function(){
    initApp()
  });
  //sendForm();
});

/*function sendForm(){
    var isTouchDevice = function() {  return 'ontouchstart' in window || 'onmsgesturechange' in window; };
    var isDesktop = window.screenX != 0 && !isTouchDevice() ? true : false;

    if(!isDesktop){
      var id = android.getDeviceID();
      console.log(id);
      document.getElementById("id_deviceID").setAttribute("value", id);
    }
}*/

function activateFirebase(){
  // Initialize Firebase
  // TODO: Replace with your project's customized code snippet
  var config = {
    apiKey: "AIzaSyCMq6ZpjMrtU7hVN2GrqeEC2RSfVhU07j8",
    authDomain: "taboo-7351f.firebaseapp.com",
    databaseURL: "https://taboo-7351f.firebaseio.com/ ",
    storageBucket: "gs://taboo-7351f.appspot.com",
    messagingSenderId: "96624224364",
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

  
    // if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    //   initApp();
    // }else{
    //  window.addEventListener('load', function(){
    //   initApp();
    //  });
  //}

  /*ui.start('#firebaseui-auth-container', {
    signInSuccessUrl = 'instructions/',
    signInOptions = [
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        {
            provider: firebase.auth.FacebookAuthProvider.PROVIDER_ID,
            scopes: [
             'public_profile',
             'email'
            ]
        },
        firebase.auth.TwitterAuthProvider.PROVIDER_ID,
        {
            provider: firebase.auth.EmailAuthProvider.PROVIDER_ID,
            requireDisplayName: true
        }
    ]
    tosUrl = 'privacy/'
  });*/
}

function initApp(){
  firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    sendToDjango(user);

    // User is signed in.
    /*var displayName = user.displayName;
    var email = user.email;
    var emailVerified = user.emailVerified;
    var photoURL = user.photoURL;
    var uid = user.uid;
    var phoneNumber = user.phoneNumber;
    var providerData = user.providerData;
    
    user.getIdToken().then(function(accessToken) {
      document.getElementById('sign-in-status').textContent = 'Signed in';
      document.getElementById('sign-in').textContent = 'Sign out';
      document.getElementById('account-details').textContent = JSON.stringify({
        displayName: displayName,
        email: email,
        emailVerified: emailVerified,
        phoneNumber: phoneNumber,
        photoURL: photoURL,
        uid: uid,
        accessToken: accessToken,
        providerData: providerData
      }, null, '  ');
    });
  } else {
    // User is signed out.
    //document.getElementById('sign-in-status').textContent = 'Signed out';
    //document.getElementById('sign-in').textContent = 'Sign in';
    document.getElementById('account-details').textContent = 'null';
  }
}, function(error) {
  console.log(error);*/
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
        console.log(disabled == "x");
        console.log(disabled === "x");
        if (disabled == "x"){
            window.location.replace("/game/disabled/") 
        }
        if (disabled == "y"){
          window.location.replace("/game/instructions/")
        }
        if (is_numeric(disabled)){
          window.location.replace("/game/recover/"+disabled+"/")
        }
        if(!disabled){
          window.location.replace("/game/instructions/")
        }
      }
    });
}

function is_numeric(str){
    return /^\d+$/.test(str);
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
