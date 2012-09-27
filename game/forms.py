from django import forms

class ConfigForm(forms.Form):
    NUMBER_OF_PLAYERS = (
        (0, 'Zero (computer vs computer)'),
        (1, 'One (human vs computer)'),
        (2, 'Two (human vs human)')
    )
    DIFFICULTIES = (
        (0, 'Normal'),
        (1, 'Hard'),
    )
    players = forms.TypedChoiceField(
                widget=forms.RadioSelect,
                choices=NUMBER_OF_PLAYERS,
                coerce=int,
                label="Number of Players",
                initial=1)
    difficulty = forms.TypedChoiceField(
                    widget=forms.RadioSelect,
                    choices=DIFFICULTIES,
                    coerce=int,
                    label="Computer Difficulty",
                    initial=0,
                    required=False)

