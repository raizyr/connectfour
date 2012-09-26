# Create your models here.
from django.conf import settings

import numpy as np
import operator as op

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
SCORES = [1,5,100,10000,2,6,200,15000]
MAX_SCORE = 5000
INFINITY = float('inf')

class Board(object):
    """State machine for a game board"""
    def __init__(self, width=None, height=None, turn=None):
        self.width = width or settings.BOARD_WIDTH
        self.height = height or settings.BOARD_HEIGHT
        self.turn = turn or PLAYERS[0]
        self.state = np.array(['_' for x in range(self.height*self.width)]).reshape(self.height,self.width)

        self.scorecache = {}

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
        if score <= -MAX_SCORE: return (None,score) # we lose
        if score >= MAX_SCORE: return (None,score) # we win

        best = (-1,-INFINITY) # best (column,score) found
        worst = (-1,INFINITY) # worst (column,score) found
        for col in range(self.width):
            try:
                self._domove(col)
                nextmove = self.minimax(player, depth-1) # look ahead depth - 1 moves
                self._undomove(col)
                if best[0] == -1 or nextmove[1] > best[1]: best = (col,nextmove[1]) # compare to previous best
                if worst[0] == -1 or nextmove[1] < worst[1]: worst = (col,nextmove[1]) # compare to previous worst
            except InvalidColumn:
                pass
        if self.turn == player:
            return (best[0],best[1]+score) # make best possible move
        else:
            return (worst[0],worst[1]+score) # make worst possible move

    def negamax(self, player, depth = None):
        if depth == None: depth = self.lookahead

        score = self._getscore(player)

        if depth == 0: return (None,score) # max depth reached, just return the score
        if score <= -MAX_SCORE: return (None,score) # we lose
        if score >= MAX_SCORE: return (None,score) # we win

        best = (-1,-INFINITY) # best (column,score) found
        for col in range(self.width):
            try:
                self._domove(col)
                nextmove = (col, -1 * self.negamax(player, depth-1)[1]) # look ahead depth - 1 moves
                self._undomove(col)
                best = max(best, nextmove, key=op.itemgetter(1)) # compare to previous best
            except InvalidColumn:
                pass
        return best

    def alphabeta(self, player, depth = None, alpha = -INFINITY, beta = INFINITY):
        if depth == None: depth = self.lookahead

        score = self._getscore(player)

        if depth <= 0: return (None,score) # max depth reached, just return the score
        if score <= -MAX_SCORE: return (None,score) # we lose
        if score >= MAX_SCORE: return (None,score) # we win

        best = (-1,-INFINITY) # best (column,score) found
        for col in range(self.width):
            try:
                self._domove(col)
                nextmove = (col, -1 * self.alphabeta(player, depth-1,-beta,-alpha)[1]) # look ahead depth - 1 moves
                self._undomove(col)
                best = max(best, nextmove, key=op.itemgetter(1)) # compare to previous best
                if (best[1] >= beta):
                    break;
                if (best[1] > alpha):
                    alpha = best[1]
            except InvalidColumn:
                pass
        return best

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
        if player+str(self.state) in self.scorecache:
            return self.scorecache[player+str(self.state)]
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
                            return SCORES[playerMarked-1]
                        elif opponentMarked == 4:
                            # we lose
                            return -SCORES[opponentMarked-1+4]
                        elif playerMarked > 0 and opponentMarked == 0:
                            # add score for player if we have cells marked and opponent does not
                            score = score + SCORES[playerMarked-1]
                        elif playerMarked == 0 and opponentMarked > 0:
                            # sub score for opponent if they have cells marked and we do not
                            score = score - SCORES[opponentMarked-1+4]
                        # don't modify score if either both have cells marked or neither do
                    except IndexError:
                        pass
        self.scorecache[player+str(self.state)] = score
        return score




    @property
    def lookahead(self):
        """
        Determine computer player's look ahead depth based on board difficulty
        """
        return 3

    @property
    def winner(self):
        """
        Return a winner if one exists by checking the current board score
        """
        score = self._getscore(self.turn)
        if score >= MAX_SCORE:
            return self.turn
        elif score <= -MAX_SCORE:
            return PLAYERS[abs(PLAYERS.index(self.turn)-1)]
        return None



