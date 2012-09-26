# Create your views here.
from django.shortcuts import render

from game.models import Board

def index(request, algo = 'minimax', diff = 1):
    # start a new board
    board = Board(algorithm=algo, difficulty=diff)
    request.session['board'] = board

    return render(request, 'game/index.html', {"board": board})
