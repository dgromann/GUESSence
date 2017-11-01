var lastTimeID = 0;

$(document).ready(function(){
  activateFirebase();
  logoutUser();
});

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
}

function logoutUser(){
	firebase.auth().signOut().then(function() {
	  console.log('Signed Out');
	}, function(error) {
  	console.error('Sign Out Error', error);
  });
}