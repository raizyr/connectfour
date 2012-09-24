# Create your models here.
from django.conf import settings

class Board(object):
    """State machine for a game board"""
    def __init__(self, width=None, height=None, turn=None, state=None):
        self.width = width or settings.BOARD_WIDTH
        self.height = height or settings.BOARD_HEIGHT
        self.turn = turn or 0
        self.state = state or list([[None for col in range(self.width)] for row in range(self.height)])

    def playcolumn(self, player, column):
        self.turn = player
