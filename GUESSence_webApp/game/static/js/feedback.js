$(document).ready(function(){
  $('#feedback-form').on('submit', function( event ){
  event.preventDefault();
  feedback();
  })
});
 
function feedback(){
  var feedback = $('#feedback').val();
  var game_id = $('#game_id').val();
  console.log(game_id)

  $.ajax({
    url: '/game/provideFeedback/'+game_id+'/',
    type: 'POST',
    data: {param: feedback},

    success: function( data ){
      window.location.replace("/game/start/logout/"+data+"/")
    }
  });
}