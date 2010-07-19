$(document).ready(function(){
	$("div[id*='careteam_block_']").hide()
	});	

function toggle_careteam_block(id) {
    var cteam_block = $('#careteam_block_' + id);
    var flipper = $('#careteam_flipper_' + id);
    
    if(cteam_block.hasClass('hidden')) {
        flipper.text("Hide People");
        cteam_block.slideDown();
    }
    else {
        flipper.text("Show People");
        cteam_block.slideUp();
    }
    cteam_block.toggleClass('hidden');
}