# Create your models here.
from django.conf import settings

import numpy as np

from game.exceptions import *

PLAYERS = ('P','C') # P for player, C for computer
# Possible WIN directions
WINS = {
    -45: { 'x': np.array([0,1,2,3]), 'y': np.array([0,-1,-2,-3]) },
     45: { 'x': np.array([0,1,2,3]), 'y': np.array([0,1,2,3]) },
      0: { 'x': np.array([0,1,2,3]), 'y': np.array([0,0,0,0]) },
     90: { 'x': np.array([0,0,0,0]), 'y': np.array([0,1,2,3])}
}

class Board(object):
    """State machine for a game board"""
    def __init__(self, width=None, height=None, turn=None):
        self.width = width or settings.BOARD_WIDTH
        self.height = height or settings.BOARD_HEIGHT
        self.turn = turn or PLAYERS[0]
        self.state = np.array(['_' for x in range(self.height*self.width)]).reshape(self.height,self.width)

    def playcolumn(self, player, column):
        if player != self.turn:
            raise InvalidPlayer # it's not your turn!
        if self.winner:
            raise GameOver
        self._swapplayer()
        self._playcolumn(player, column)

    def _playcolumn(self, p, c):
        """Update the board state for a column"""
        try:
            # Slice the board state to the specified column
            # state[:,c]
            # Filter it to only cells containing '_'
            # (state[:,c] == '_').nonzero()[0]
            # and then get highest indexed item for the row
            r = (self.state[:,c] == '_').nonzero()[0].max()
            self.state[r,c] = p
        except ValueError:
            raise InvalidColumn

    def _swapplayer(self):
        self.turn = PLAYERS[abs(PLAYERS.index(self.turn)-1)]

    @property
    def winner(self):
        (r,c) = self.state.shape
        for i in range(r):
            for j in range(c):
                for direction in WINS.keys():
                    try:
                        slice = self.state[WINS[direction]['x']+i,WINS[direction]['y']+j]
                        for player in PLAYERS:
                            if np.all(slice == player):
                                return player
                    except IndexError:
                        pass
        return None



