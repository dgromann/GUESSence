/*
Main method to transfer data between frontend and Firebase 
to Django backend
*/
var lastTimeID = 0;

$(document).ready(function(){
  $('#reported').hide();
  startChat();
});

$('#next').on('submit', function( event ){
  event.preventDefault();
  window.location.replace("next/") 
});

$('#start').on('submit', function( event ){
  event.preventDefault();
  window.location.replace("start/") 
});

$('#game-form').on('submit', function( event ){
  event.preventDefault();
  $('#alertInfo').show();
  $('#unknownCity').hide();
  checkChatText();
});

$('#reported').click(function (event) {
  event.preventDefault();
  assureReporting();
});

$('#user-form').on('submit', function( event ){
  event.preventDefault();
});

function assureReporting(){
  var game_id = $('#game_id').val();
  bootbox.confirm({
    title: "Warning",
    message: "Are you sure you want to report the other user? Is the message really abusive?",
    buttons: {
    cancel: {
       label: '<i class="fa fa-times"></i> No, do not report'
    },
    confirm: {
      label: '<i class="fa fa-check"></i> Yes, report'
    }
  },
  callback: function (result) {
  if (result){
      window.location.replace("/game/reported/"+game_id+"/")
    }
    }
  });
}

function checkChatText( ){
  var chatInput = $('#chatInput').val();
  var game_id = $('#game_id').val();

  $.ajax({
      url: '/game/warning/'+game_id+'/',
      type: 'POST',
      data: {param: chatInput},


      success: function( data ){
        if (data != "None"){
            if (data.substring(0, 7) == "WARNING"){
              $('#alertInfo').hide();
              bootbox.confirm({
                  title: "Warning",
                  message: data,
                  buttons: {
                  cancel: {
                     label: '<i class="fa fa-times"></i> Modify'
                  },
                  confirm: {
                    label: '<i class="fa fa-check"></i> Submit as is'
                  }
             },
              callback: function (result) {
                if (result){
                  sendChatText( chatInput );
                }
              }
              });
            }
            if (data.substring(0, 8) == "Spelling"){
              $('#alertInfo').hide();
              bootbox.confirm({
                  title: "Spelling",
                  message: data,
                  buttons: {
                  cancel: {
                     label: '<i class="fa fa-times"></i> Change spelling'
                  },
                  confirm: {
                    label: '<i class="fa fa-check"></i> Submit as is'
                  }
             },
              callback: function (result) {
                if (result){
                  var input = data.substring(data.indexOf("instead of ")+11, data.indexOf("?"));
                  sendChatText( input );
                }
                else{
                  var corrected = data.substring(23, data.indexOf(" instead"));
                  sendChatText( corrected );
                  //checkChatText(corrected);
                }
              }
              });
            }
            else{
              if (data.substring(0, 7) !== "WARNING"){
                $('#alertInfo').hide();
                bootbox.alert({
                    title: "Warning",
                    message: data,
                });
              }
            }
        }else{
          sendChatText(chatInput);
        }
      }
    });
}

function displayTime( ){
  var game_id = $('#game_id').val();
  var refreshInterval; 

  if(refreshInterval){
    clearInterval(refreshInterval)
  }
  else{
    refreshInterval = setInterval( function() { 
    $.ajax({
      url: '/game/timer/'+game_id+'/',
      type: 'POST',

      success: function( data  ){
        if (data != "None"){
          data = data.slice(2, data.length-7);
          $('#countdown').html(data);
          $('#reported').show();
        }
        if (data == "00:00"){
          window.location.replace("/game/timeout/"+game_id+"/")
        }
        else{
          data = "";
        }
      }
    });
  }, 1000);
  }
}

function sendChatText( chatInput ){
  var game_id = $('#game_id').val();
  
  $.ajax({
      url: '/game/'+game_id+'/',
      type: 'POST',
      data: {param: chatInput},

      success: function( data ){
        $('#alertInfo').hide();
        $('#chatInput').val("");
        $('#response').html(data);
       }
    });
} 

function startChat(){
  var chatInput = $('#chatInput').val();
  
  if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    getChatText();
    getPlayer();
    playersOnline();
    getPlayersScores();
  }else{
    setInterval( function() { 
      getChatText();
      getPlayer();
      playersOnline();
      getPlayersScores();
    }, 1000);
  }
  
}

function getChatText() {
  var game_id = $('#game_id').val();

  $.ajax({
      url: '/game/update/'+game_id+'/',
      type: 'POST',

    success: function( data ){
      if (is_numeric(data)){
        window.location.replace("/game/start/success/"+data+"/")
      }
      if (data[0] == "x"){
        data = data.slice(1, data.length);
        window.location.replace("/game/unknown/"+data+"/")
      }
      if (data[0] == "y"){
        data = data.slice(1, data.length);
        window.location.replace("/game/timeout/"+data+"/")
      }
      if (data[0] == "z"){
        data = data.slice(1, data.length);
        window.location.replace("/game/reported_redirect/"+data+"/")
      }
      else{
        $('#response').html(data);
        displayTime();
      }
    }
  });
}

function is_numeric(str){
    return /^\d+$/.test(str);
}

function getPlayer(){
  var game_id = $('#game_id').val();
  
  $.ajax({
    url: '/game/player/'+game_id+'/',
    type: 'POST',
    success: function( data  ){
      $('#playersAvailable').html(data);
    }
  });
}

function playersOnline(){
  $.ajax({
    url: '/game/players/',
    type: 'POST',
    success: function( data ){
      $('#playersOnline').html(data);
    }
  });
}

function getPlayersScores(){
  $.ajax({
    url: '/game/scores/',
    type: 'POST',
    success: function ( data ){
      var userscore = data.substring(3,data.indexOf("yyy"));
      $('#myScore').html(userscore);
      var otherscores = data.substring(data.indexOf("yyy")+3, data.length);
      $('#bestFive').html(otherscores);
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

