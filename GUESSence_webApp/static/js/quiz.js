/*$(document).ready(function( ) {

	$(".alerts").on('click', function() {
		var did=$(this).attr('data-id');
		console.log(did)
		$('#response').append("Wrong");
	});
});*/

$(".alerts").on('click',function() {
    
    var did=$(this).attr('data-id');
        $(document).trigger("set-alert-id-"+did, [
        {
            'message': "Wrong",
            'priority': 'warning'
        }]);
    });

$(".correct").on('click',function() {
    
    var did=$(this).attr('data-id');
        $(document).trigger("set-alert-id-"+did, [
        {
            'message': "Yes! Exactly!",
            'priority': 'warning'
        }]);
    });