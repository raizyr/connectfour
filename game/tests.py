"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from django.conf import settings
from game.models import Board, PLAYERS


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class BoardTest(TestCase):
    def setUp(self):
        self.board = Board()

    def teardown(self):
        pass

    def test_default_board(self):
        """
        Test that creating a board sets proper defaults
        """
        board = Board()
        self.assertEqual(board.width, settings.BOARD_WIDTH)
        self.assertEqual(board.height, settings.BOARD_HEIGHT)
        self.assertEqual(board.turn, 'P')
        self.assertEqual(board.state.size, board.height*board.width)

    def test_board(self):
        """
        Test creating a board with options
        """
        board = Board(width=10,height=11)
        self.assertEqual(board.width, 10)
        self.assertEqual(board.height, 11)
        self.assertEqual(board.state.size, board.height*board.width)

    def test_playcolumn_swaps_player_turn(self):
        currentPlayer = self.board.turn
        if currentPlayer == PLAYERS['player']:
            self.board.playcolumn('player', 3)
            self.assertEqual(self.board.turn, PLAYERS['computer'])
        else:
            self.board.playcolumn('computer', 3)
            self.assertEqual(self.board.turn, PLAYERS['player'])

