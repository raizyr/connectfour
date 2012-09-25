"""
Game specific exceptions
"""

class InvalidPlayer(Exception):
    """The player is not the current allowed player"""
    pass

class GameOver(Exception):
    """The game is already complete"""
    pass

class InvalidColumn(Exception):
    """The column is not valid for play"""
    pass

