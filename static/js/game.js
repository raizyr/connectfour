$(document).ready(function(){
  $('#board').on('nextplayer', function(e) {
    var turn = $('#board').data('turn')
    if ($('#board').data('player') == 'C') {
      $('#gamestatus h1').text(playertext[turn] + " computer player is thinking.");
      Dajaxice.game.playcolumn(Dajax.process, {'column': null});
    } else {
      $('#gamestatus h1').text(playertext[turn] + " player's turn!");
    }
  });
  $("#board").delegate('td','mouseover mouseleave', function(e) {
    var turn = $('#board').data('turn')
    if (e.type == 'mouseover' && $('#board').data('player') == 'P') {
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played)").addClass("hover");
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played):last").addClass("hover-target" + turn);
    } else {
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played)").removeClass("hover");
      $("#board tr td:nth-child("+($(this).index()+1)+"):not(.played):last").removeClass("hover-target" + turn);
    }
  });

  $('td.gamecell').click(function(e){
    if ($('#board').data('player') == 'P') {
      console.log('playing column ' + $(this).data('column'));
      Dajaxice.game.playcolumn(Dajax.process, {'column':$(this).data('column')});
    }
  });

  // trigger nextplayer event if a computer player is starting
  if ($('#board').data('player') == 'C') {
    $('#board').trigger('nextplayer');
  }

  $('form input:radio[name="players"]').on('change', function(e){
    var d = $(this).val() == 2 ? true: false;
    $('form input:radio[name="difficulty"]').prop('disabled', d);
  });
});


var playertext = {"R":"Red", "B":"Black", "D":"Draw! No"}

var update_game_status = function(data) {
  if (data['winner']) {
    $('#board').removeData(['turn', 'player']);
    $('#gamestatus h1').text("Game Over!  " + playertext[data['winner']] + " player wins!");
    $('#gamestatus').append($('<a href="/">Click here to play again.</a>'));
  } else {
    $('#board').data(data).trigger('nextplayer');
  }
}
