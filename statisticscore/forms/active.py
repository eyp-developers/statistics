from django import forms


class ActiveDebateForm(forms.Form):
    #The Active Debate form is another more complex one, as it requires an array of the avaliable debates to chose from.
    #This is set up in the same way as the Point form, with a custom extra argument.
    def __init__(self, active_debate_choices, *args, **kwargs):
        super(ActiveDebateForm, self).__init__(*args, **kwargs)
        self.fields['active_debate'].choices = active_debate_choices

    #This is the same as the point form, the same normal data with an empty choices argument.
    session = forms.CharField(max_length=100, required=True)
    active_debate = forms.ChoiceField(choices=(), required=True)

class ActiveRoundForm(forms.Form):
    #Same as the Active Debate form, a custom argument for the rounds. There can't just be a maximum round number,
    #there has to be an array with the name (number) of each round.
    def __init__(self, active_round_choices, *args, **kwargs):
        super(ActiveRoundForm, self).__init__(*args, **kwargs)
        self.fields['active_round'].choices = active_round_choices

    #Setting up arguments again.
    session = forms.CharField(max_length=100, required=True)
    active_round = forms.ChoiceField(choices=(), required=True)
