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
    def __init__(self, width=None, height=None, turn=None, algorithm='alphabeta', difficulty=None):
        self.width = width or settings.BOARD_WIDTH
        self.height = height or settings.BOARD_HEIGHT
        self.turn = turn or PLAYERS[0]
        self.state = np.array(['_' for x in range(self.height*self.width)]).reshape(self.height,self.width)
        self.algorithm = algorithm
        self.difficulty = difficulty or 1

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
        if depth is None: depth = self.lookahead

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = self.minimax_value(player, depth)
            self._undomove(move)
            if best is None or val > best[1]:
                best = (move, val)

        return best

    def minimax_value(self, player, depth):
        score = self._getscore(player)

        # return the score if we've hit max depth or either won or lost the game
        if depth <= 0 or abs(score) >= MAX_SCORE: return score

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = self.minimax_value(player, depth-1)
            self._undomove(move)
            if self.turn == player:
                best = max(val,best) # our turn so use the best move
            else:
                best = min(val,best) # opponent's turn so use the worst move

        return best

    def negamax(self, player, depth = None):
        """Determine the best move for player"""
        if depth is None: depth = self.lookahead

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = -1 * self.negamax_value(player, depth)
            self._undomove(move)
            if best is None or val > best[1]:
                best = (move, val)

        return best

    def negamax_value(self, player, depth):
        score = self._getscore(player)

        # return the score if we've hit max depth or either won or lost the game
        if depth <= 0 or abs(score) >= MAX_SCORE: 
            if player == self.turn:
                return score
            else:
                return -score

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = -1 * self.negamax_value(player, depth-1)
            self._undomove(move)
            if best is None or val > best:
                best = val

        return best

    def alphabeta(self, player, depth=None):
        best_val, best_move = None, None
        if depth is None: depth = self.lookahead

        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            if best_val is not None:
                opp_beta = -1 * best_val
            else:
                opp_beta = None
            val = -1 * self.alphabeta_value(player, depth, None, opp_beta)
            self._undomove(move)
            # update the best move so far
            if best_val is None or val > best_val:
                (best_move, best_val) = (move, val)

        return (best_move, best_val)

    def alphabeta_value(self, player, depth, alpha, beta):
        score = self._getscore(player)

        # return the score if we've hit max depth or either won or lost the game
        if depth <= 0 or abs(score) >= MAX_SCORE:
            if player == self.turn:
                return score
            else:
                return -score

        # one possible move per column
        for move in self._movesgenerator():
            self._domove(move)
            if beta is not None:
                opp_alpha = -1 * beta
            else:
                opp_alpha = None
            if alpha is not None:
                opp_beta = -1 * alpha
            else:
                opp_beta = None
            val = -1 * self.alphabeta_value(player, depth-1, opp_alpha, opp_beta)
            self._undomove(move)
            # update alpha (current player's low bound)
            if alpha is None or val > alpha:
                alpha = val
            # prune using the alpha-beta condition
            if (alpha is not None) and (beta is not None) and alpha >= beta:
                return beta
        # alpha is the best score
        return alpha

    def _movesgenerator(self):
        for col in range(self.width):
            if self._checkmove(col): yield col

    def _checkmove(self, c):
        return (self.state[:,c] == '_').any()

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

    def computermove(self, player):
        return getattr(self, self.algorithm)(player)[0]


    @property
    def lookahead(self):
        """
        Determine computer player's look ahead depth based on board difficulty
        """
        return self.difficulty

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



