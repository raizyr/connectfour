# Create your views here.
from django.shortcuts import render

from game.models import Board
from game.forms import ConfigForm

def index(request):
    (diff, players) = (None, 1)
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            diff = form.cleaned_data['difficulty']
            players = form.cleaned_data['players']
    # start a new board
    board = Board(difficulty=diff, players=players)
    request.session['board'] = board

    return render(request, 'game/index.html', {"board": board})

def home(request):
    form = ConfigForm()
    return render(request, 'game/home.html', {"form":form})
