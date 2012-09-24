from django.core.context_processors import csrf

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from game.models import Board

@dajaxice_register
def playcolumn(request, column):
    board = request.session.get('board')
    player = board.turn
    board.playcolumn(1, column)

    dajax = Dajax()
    dajax.assign('#board', 'data-turn', board.turn)
    cell_selector = '#board tr td:nth-child(%s):not(.played):last' % str(column + 1)
    dajax.add_css_class(cell_selector, ['player%s' % str(player), 'played'])
    dajax.remove_css_class('#board td', ['hover', 'hover-target'])

    return dajax.json()
