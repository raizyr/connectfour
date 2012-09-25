# Create your models here.
from django.conf import settings

import numpy as np

# Characters for Player & Computer used in board state
PLAYERS = {
'player': 'P',
'computer': 'C'
}

class Board(object):
    """State machine for a game board"""
    def __init__(self, width=None, height=None, turn=None, state=None):
        self.width = width or settings.BOARD_WIDTH
        self.height = height or settings.BOARD_HEIGHT
        self.turn = turn or PLAYERS['player']
        self.state = state or np.array(['_' for x in range(self.height*self.width)]).reshape(self.height,self.width)

    def playcolumn(self, player, column):
        self.turn = [v for k,v in PLAYERS.iteritems() if k != 'player'][0]
