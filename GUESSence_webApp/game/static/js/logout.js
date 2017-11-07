var lastTimeID = 0;

$(document).ready(function(){
  activateFirebase();
  logoutUser();
});

function activateFirebase(){
  // Initialize Firebase
  // TODO: Replace with your project's customized code snippet
  var config = {
    apiKey: "your key",
    authDomain: "your id.firebaseapp.com",
    databaseURL: "https://your-id.firebaseio.com/ ",
    storageBucket: "gs://your-id.appspot.com",
    messagingSenderId: "your sender id",
  };
  firebase.initializeApp(config);
}

function logoutUser(){
	firebase.auth().signOut().then(function() {
	  console.log('Signed Out');
	}, function(error) {
  	console.error('Sign Out Error', error);
  });
}