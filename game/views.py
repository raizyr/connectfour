# Create your views here.
from django.shortcuts import render

from game.models import Board

def index(request):
    # start a new board
    board = Board()
    request.session['board'] = board

    return render(request, 'game/index.html', {"board": board})
