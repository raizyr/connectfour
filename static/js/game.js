$(document).ready(function(){
  $('#board').on('turnchanged', function(e) {
    if ($('#board').data('turn') == 'C') {
      $('#gamestatus h1').text("Computer is thinking.");
      Dajaxice.game.computerplay(Dajax.process);
    } else {
      $('#gamestatus h1').text("Your turn!");
    }
  });
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

var wintext = {"C":"Computer wins!", "P":"You win!"}

var update_game_status = function(data) {
  if (data['winner']) {
    $('#board').removeData('turn');
    $('#gamestatus h1').text("Game Over!  " + wintext[data['winner']]);
    $('#gamestatus').append($('<a href="/game/">Click here to play again.</a>'));
  } else {
    $('#board').data('turn', data['turn']).trigger('turnchanged');
  }
}
