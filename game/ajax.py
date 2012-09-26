from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

@dajaxice_register
def playcolumn(request, column):
    board = request.session.get('board')
    board.playcolumn('P', column)
    request.session['board'] = board

    dajax = Dajax()
    dajax.add_data({'turn':board.turn, 'winner':board.winner}, 'update_game_status')
    cell_selector = '#board tr td:nth-child(%s):not(.played):last' % str(column + 1)
    dajax.add_css_class(cell_selector, ['player', 'played'])
    dajax.remove_css_class('#board td', ['hover', 'hover-target'])

    return dajax.json()

@dajaxice_register
def computerplay(request):
    board = request.session.get('board')
    column = board.playcolumn('C', board.computermove('C'))
    request.session['board'] = board

    dajax = Dajax()
    dajax.add_data({'turn':board.turn, 'winner':board.winner}, 'update_game_status')
    cell_selector = '#board tr td:nth-child(%s):not(.played):last' % str(column + 1)
    dajax.add_css_class(cell_selector, ['computer', 'played'])
    dajax.remove_css_class('#board td', ['hover', 'hover-target'])

    return dajax.json()
