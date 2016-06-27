$(document).ready(function() {
		
	$('#likes').click(function(){
        //alert("You clicked the button using JQuery!");
	    var catid;
	    catid = $(this).attr("data-catid"); // extract the category id from this button
	    $.get('/rango/like_category/', {category_id: catid}, function(data){
	               $('#like_count').html(data); // update the new count
	               $('#likes').hide(); // hide the Like button
	    });
	});

	$('#suggestion').keyup(function(){
	        var query;
	        query = $(this).val();
	        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
	         $('#cats').html(data);
	        });
	});
});