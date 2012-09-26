from django.core.context_processors import csrf

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from game.models import Board

@dajaxice_register
def playcolumn(request, column):
    board = request.session.get('board')
    board.playcolumn('P', column)
    request.session['board'] = board

    dajax = Dajax()
    dajax.add_data(board.turn, 'change_board_turn')
    cell_selector = '#board tr td:nth-child(%s):not(.played):last' % str(column + 1)
    dajax.add_css_class(cell_selector, ['player', 'played'])
    dajax.remove_css_class('#board td', ['hover', 'hover-target'])
    dajax.add_data(None, 'computer_turn')

    return dajax.json()

@dajaxice_register
def computerplay(request):
    board = request.session.get('board')
    column = board.playcolumn('C', board.minimax('C')[0])
    request.session['board'] = board

    dajax = Dajax()
    dajax.add_data(board.turn, 'change_board_turn')
    cell_selector = '#board tr td:nth-child(%s):not(.played):last' % str(column + 1)
    dajax.add_css_class(cell_selector, ['computer', 'played'])
    dajax.remove_css_class('#board td', ['hover', 'hover-target'])

    return dajax.json()
