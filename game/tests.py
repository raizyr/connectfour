"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings

from random import choice
import numpy as np

from game.models import Board, PLAYERS
from game import exceptions as e


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class BoardTest(TestCase):
    def setUp(self):
        self.board = Board()

        self.overboard = Board()
        self.overboard.state[-4:,3] = 'C'

        self.fullboard = Board()
        self.fullboard.state[3:,2] = 'C'
        self.fullboard.state[:-3,2] = 'P'

    def teardown(self):
        pass

    def test_default_board(self):
        """
        Test that creating a board sets proper defaults
        """
        board = Board()
        self.assertEqual(board.width, settings.BOARD_WIDTH, 'Board width does not match default value')
        self.assertEqual(board.height, settings.BOARD_HEIGHT, 'Board height does not match default value')
        self.assertEqual(board.turn, PLAYERS[0], 'Board current turn does not match default value')
        self.assertEqual(board.state.size, board.height*board.width, 'Board state does not match expected state')

    def test_board(self):
        """
        Test creating a board with options
        """
        board = Board(width=10,height=11)
        self.assertEqual(board.width, 10, 'Board width does not match passed value')
        self.assertEqual(board.height, 11, 'Board height does not match passed value')
        self.assertEqual(board.state.size, board.height*board.width, 'Board state does not match expected state')

    def test_playcolumn_raises_InvalidPlayer_on_invalid_player(self):
        invalidPlayer = PLAYERS[abs(PLAYERS.index(self.board.turn)-1)]
        self.assertRaises(e.InvalidPlayer, self.board.playcolumn, invalidPlayer, 3)


    def test_playcolumn_swaps_player_turn(self):
        currentPlayer = self.board.turn
        self.board.playcolumn(currentPlayer, 3)
        self.assertNotEqual(self.board.turn, currentPlayer, 'Board player did not change')

    def test_playcolumn_changes_board_state(self):
        currentState = self.board.state.copy()
        self.board.playcolumn(self.board.turn, choice(range(self.board.width)))
        self.assertNotEqual(self.board.state.size, np.sum(currentState == self.board.state), 'Board state did not change')

    def test_playcolumn_raises_GameOver_when_game_complete(self):
        self.assertRaises(e.GameOver, self.overboard.playcolumn, self.overboard.turn, 2)

    def test_playcolumn_raises_InvalidColumn_when_column_is_full(self):
        self.assertRaises(e.InvalidColumn, self.fullboard.playcolumn, self.fullboard.turn, 2)



