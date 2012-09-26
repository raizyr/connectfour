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

# Scoring weights
SCORES = [0,2,8,64]
MAX_SCORE = 99999

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
        self._domove(column)
        return column

    def _nextplayer(self):
        self.turn = PLAYERS[abs(PLAYERS.index(self.turn)-1)]

    def minimax(self, player, depth = None):
        """Determine the best move for player"""
        if depth == None: depth = self.lookahead

        score = self._getscore(player)

        if depth == 0: return (None,score) # max depth reached, just return the score
        if score == -MAX_SCORE: return (None,score) # we lose
        if score == MAX_SCORE: return (None,score) # we win

        best = (-1,0) # best (column,score) found
        worst = (-1,999999) # worst (column,score) found
        for col in range(self.width):
            try:
                self._domove(col)
                nextmove = self.minimax(player, depth-1) # look ahead depth - 1 moves
                self._undomove(col)
                if best[0] == -1 or nextmove[1] > best[1]: best = (col,nextmove[1]) # compare to previous best
                if worst[0] == -1 or nextmove[1] < worst[1]: worst = (col,nextmove[1]) # compare to previous worst
            except InvalidColumn:
                pass
#        import pdb; pdb.set_trace()
        if self.turn == player:
            return (best[0],best[1]+score) # make best possible move
        else:
            return (worst[0],worst[1]+score) # make worst possible move

    def _domove(self, c):
        try:
            # Slice the board state to the specified column
            # state[:,c]
            # Filter it to only cells containing '_'
            # (state[:,c] == '_').nonzero()[0]
            # and then get highest indexed item for the row
            r = (self.state[:,c] == '_').nonzero()[0].max()
            self.state[r,c] = self.turn
            self._nextplayer()
        except ValueError:
            raise InvalidColumn

    def _undomove(self, c):
        try:
            # Slice the board state to the specified column
            # state[:,c]
            # Filter it to cells containing any player marker
            # (state[:,c] != '_').nonzero()[0]
            # and then get lowest indexed item for the row
            r = (self.state[:,c] != '_').nonzero()[0].min()
            self.state[r,c] = '_'
            self._nextplayer()
        except ValueError:
            raise InvalidColumn

    def _getscore(self, player):
        score = 0
        (r,c) = self.state.shape
        for i in range(r):
            for j in range(c):
                for direction in WINS.keys():
                    try:
                        slice = self.state[WINS[direction]['x']+i,WINS[direction]['y']+j]
                        # number of cells we have marked
                        playerMarked = np.sum(slice == player)
                        # number of cells opponent has marked
                        opponentMarked = np.sum(slice == PLAYERS[abs(PLAYERS.index(player)-1)])
                        if playerMarked == 4:
                            # we win
                            return MAX_SCORE
                        elif opponentMarked == 4:
                            # we lose
                            return -MAX_SCORE
                        elif playerMarked > 0 and opponentMarked == 0:
                            # add score for player if we have cells marked and opponent does not
                            score = score + SCORES[playerMarked]**2
                        elif playerMarked == 0 and opponentMarked > 0:
                            # sub score for opponent if they have cells marked and we do not
                            score = score - SCORES[opponentMarked]**2
                        # don't modify score if either both have cells marked or neither do
                    except IndexError:
                        pass
        return score




    @property
    def lookahead(self):
        """
        Determine computer player's look ahead depth based on board difficulty
        """
        return 2

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



