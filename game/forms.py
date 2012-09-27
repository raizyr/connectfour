from django import forms

from game.models import DIFFICULTIES as D, PLAYER_COMBINATIONS as P

class ConfigForm(forms.Form):
    players = forms.TypedChoiceField(
                widget=forms.RadioSelect,
                choices=[(k,v[1]) for k,v in enumerate(P)],
                coerce=int,
                label="Number of Players",
                initial=1)
    difficulty = forms.TypedChoiceField(
                    widget=forms.RadioSelect,
                    choices=[(k,v[2]) for k,v in enumerate(D)],
                    coerce=int,
                    label="Computer Difficulty",
                    initial=0,
                    required=False)

