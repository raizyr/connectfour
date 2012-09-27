# Create your models here.
from django.conf import settings
from django.core.cache import get_cache

import numpy as np
import random, md5

from game import exceptions as e

PLAYERS = ('R','B') # R for red player, B for black player
PLAYER_COMBINATIONS = ( # tuples of (characterpairs, formtext)
    (('C','C'), 'Zero (computer vs computer)'),
    (('P','C'), 'One (human vs computer)'),
    (('P','P'), 'Two (human vs human)'),
)
# Possible WIN directions
WINS = {
    -45: { 'x': np.array([0,1,2,3]), 'y': np.array([0,-1,-2,-3]) },
     45: { 'x': np.array([0,1,2,3]), 'y': np.array([0,1,2,3]) },
      0: { 'x': np.array([0,1,2,3]), 'y': np.array([0,0,0,0]) },
     90: { 'x': np.array([0,0,0,0]), 'y': np.array([0,1,2,3])}
}

# Scoring weights
SCORES = [
    1, 5, 100, 10000, # moves good for current player
    2, 6, 200, 15000  # moves good for opponent higher to ensure blocking
]
MAX_SCORE = 5000
INFINITY = float('inf')

DIFFICULTIES = ( # tuples of (algorithm, lookahead, formtext)
        ('minimax', 1, 'minimax Normal (lookahead:1)'),
        ('minimax', 2, 'minimax Hard (lookahead:2)'),
        ('negamax', 1, 'negamax Normal (lookahead:1)'),
        ('negamax', 2, 'negamax Hard (lookahead:2)'),
        ('alphabeta', 1, 'alphabeta Normal (lookahead:1)'),
        ('alphabeta', 3, 'alphabeta Hard (lookahead:3)'),
)

# store scorecache directly rather than as part of the object
scorecache = get_cache('default')

class Board(object):
    """State machine for a game board"""
    def __init__(self, width=None, height=None, difficulty=0, players=1):
        """
        The game board.  Acts as a state machine for the game
        """
        self.width = width or settings.BOARD_WIDTH
        self.height = height or settings.BOARD_HEIGHT
        self.turn = PLAYERS[0]
        self.state = np.array(['_' for x in range(self.height*self.width)]).reshape(self.height,self.width)
        self.difficulty = difficulty

        # allow for 0, 1, or 2 players
        if players in (0,1,2):
            self.players = list(PLAYER_COMBINATIONS[players][0])
        else:
            self.players = list(PLAYER_COMBINATIONS[1][0])

        # randomize starting player
        random.shuffle(self.players)

    def playcolumn(self, player, column):
        """
        Make a move in a column
        """
        if player != self.turn:
            raise e.InvalidPlayer # it's not your turn!
        if self.winner:
            raise e.GameOver
        self._domove(column)
        return column

    def computermove(self, player, algorithm = None):
        """
        Determine the best move by using the defined algorithm
        """
        if algorithm is None: algorithm = self.algorithm
        return getattr(self, algorithm)(player)[0]

    def minimax(self, player, depth = None):
        """
        Determine the best move for player using minimax search algorithm
        """
        if depth is None: depth = self.lookahead

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = self._minimax_value(player, depth)
            self._undomove(move)
            if best is None or val > best[1]:
                best = (move, val)

        return best

    def negamax(self, player, depth = None):
        """
        Determine the best move for player using negamax search algorithm
        """
        if depth is None: depth = self.lookahead

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = -1 * self._negamax_value(player, depth)
            self._undomove(move)
            if best is None or val > best[1]:
                best = (move, val)

        return best

    def alphabeta(self, player, depth=None):
        """
        Determine the best move for player using alphabeta pruning algorithm
        """
        best_val, best_move = None, None
        if depth is None: depth = self.lookahead

        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            if best_val is not None:
                opp_beta = -1 * best_val
            else:
                opp_beta = None
            val = -1 * self._alphabeta_value(player, depth, None, opp_beta)
            self._undomove(move)
            # update the best move so far
            if best_val is None or val > best_val:
                (best_move, best_val) = (move, val)

        return (best_move, best_val)

    ### "Private" methods, these should not be called from outside the instance ###
    def _nextplayer(self):
        """
        Change the turn to the next player
        """
        self.turn = PLAYERS[abs(PLAYERS.index(self.turn)-1)]

    def _minimax_value(self, player, depth):
        """
        Look ahead using minimax algorithm to determine the best move
        """
        score = self._getscore(player)

        # return the score if we've hit max depth or either won or lost the game
        if depth <= 0 or abs(score) >= MAX_SCORE or self.boardfull: return score

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = self._minimax_value(player, depth-1)
            self._undomove(move)
            if self.turn == player:
                best = max(val,best) # our turn so use the best move
            elif best is None: # handles the fact that min returns None no matter the val
                best = val
            else:
                best = min(val,best) # opponent's turn so use the worst move

        return best

    def _negamax_value(self, player, depth):
        """
        Look ahead using negamax algorithm to determine the best move
        """
        score = self._getscore(player)

        # return the score if we've hit max depth or either won or lost the game
        if depth <= 0 or abs(score) >= MAX_SCORE or self.boardfull:
            if player == self.turn:
                return score
            else:
                return -score

        best = None
        # try each move
        for move in self._movesgenerator():
            self._domove(move)
            val = -1 * self._negamax_value(player, depth-1)
            self._undomove(move)
            if best is None or val > best:
                best = val

        return best

    def _alphabeta_value(self, player, depth, alpha, beta):
        """
        Look ahead using alphabeta pruning algorithm to determine best move
        """
        score = self._getscore(player)

        # return the score if we've hit max depth or either won or lost the game
        if depth <= 0 or abs(score) >= MAX_SCORE or self.boardfull:
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
            val = -1 * self._alphabeta_value(player, depth-1, opp_alpha, opp_beta)
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
        """
        Generator to yield valid moves
        """
        for col in range(self.width):
            if self._checkmove(col): yield col

    def _checkmove(self, c):
        """
        Check a column for valid moves
        """
        return (self.state[:,c] == '_').any()

    def _domove(self, c):
        """
        Attempt to make a move at column c
        """
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
            raise e.InvalidColumn

    def _undomove(self, c):
        """
        Undo last move at column c
        """
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
            raise e.InvalidColumn

    def _getscore(self, player):
        """
        Walk through all possible win conditions and calculate a total score for a particular player
        """
        cachekey = md5.new(player+str(self.state)).hexdigest()
        cached = scorecache.get(cachekey)
        if cached:
            return cached

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
                            score += SCORES[playerMarked-1]
                        elif playerMarked == 0 and opponentMarked > 0:
                            # sub score for opponent if they have cells marked and we do not
                            score -= SCORES[opponentMarked-1+4]
                        # don't modify score if either both have cells marked or neither do
                    except IndexError:
                        pass
        # add some randomness so that the computer isn't playing exactly the same every time
        score *= random.random()
        scorecache.set(cachekey, score)
        return score

    @property
    def boardfull(self):
        """
        Return True if the game board is full
        """
        return (self.state[:] != '_').all()

    @property
    def currentplayer(self):
        """
        Return the current player type based on the current turn
        """
        return self.players[PLAYERS.index(self.turn)]

    @property
    def lookahead(self):
        """
        Determine computer player's look ahead depth based on board difficulty
        """
        return DIFFICULTIES[self.difficulty][1]

    @property
    def algorithm(self):
        """
        Determine computer player's algorithm based on board difficulty
        """
        return DIFFICULTIES[self.difficulty][0]

    @property
    def winner(self):
        """
        Return a winner if one exists by checking the current board score
        """
        if self.boardfull:
            return 'D'
        score = self._getscore(self.turn)
        if score >= MAX_SCORE:
            return self.turn
        elif score <= -MAX_SCORE:
            return PLAYERS[abs(PLAYERS.index(self.turn)-1)]
        return None



