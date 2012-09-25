$(document).ready(function(){
  $("#board").delegate('td','mouseover mouseleave', function(e) {
    if (e.type == 'mouseover' && $('#board').data('turn') == 'P') {
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played)").addClass("hover");
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played):last").addClass("hover-target");
    } else {
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played)").removeClass("hover");
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played):last").removeClass("hover-target");
    }
  });

  $('td.gamecell').click(function(e){
    if ($('#board').data('turn') == 'P') {
      console.log('playing column ' + $(this).data('column'));
      Dajaxice.game.playcolumn(Dajax.process, {'column':$(this).data('column')});
    }
  });
});


var change_board_turn = function(player) {
  $('#board').data('turn', player);
}
