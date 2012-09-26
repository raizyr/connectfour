from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

@dajaxice_register
def playcolumn(request, column = None):
    board = request.session.get('board')
    player = board.turn
    if column is None:
        column = board.playcolumn(player, board.computermove(player))
    else:
        board.playcolumn(player, column)
    request.session['board'] = board

    dajax = Dajax()
    data = {'turn':board.turn, 'winner':board.winner, 'player':board.currentplayer}
    dajax.add_data(data, 'update_game_status')
    cell_selector = '#board tr td:nth-child(%s):not(.played):last' % str(column + 1)
    dajax.add_css_class(cell_selector, ['player%s' % player, 'played'])
    dajax.remove_css_class('#board td', ['hover', 'hover-target'])

    return dajax.json()
