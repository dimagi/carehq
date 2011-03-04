$(document).ready(function(){
	$("form[id*='comment_form_']").hide()
	});

	

function toggle_comment_form(id) {
    var cform = $('#comment_form_' + id);
    if(cform.hasClass('hidden')) {
        cform.prev().text("Cancel Comment");
        cform.slideDown();
    }
    else {
        cform.prev().text("Add Comment");
        cform.slideUp();
    }
    cform.toggleClass('hidden');
}