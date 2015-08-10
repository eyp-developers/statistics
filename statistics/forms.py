from django import forms

class PointForm(forms.Form):
    def __init__(self, subtopic_choices, *args, **kwargs):
        super(PointForm, self).__init__(*args, **kwargs)
        self.fields['subtopics'].choices = subtopic_choices

    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )
    session = forms.CharField(max_length=100, required=True)
    committee = forms.CharField(max_length=7, required=True)
    debate = forms.CharField(max_length=7, required=True)
    round_no = forms.IntegerField(min_value=0, required=True)
    point_type = forms.ChoiceField(choices=POINT_TYPES, required=True)
    subtopics = forms.MultipleChoiceField(choices=(), required=True)

class VoteForm(forms.Form):
    session = forms.CharField(max_length=100, required=True)
    committee = forms.CharField(max_length=7, required=True)
    debate = forms.CharField(max_length=7, required=True)
    in_favour = forms.IntegerField(min_value=0, required=True)
    against = forms.IntegerField(min_value=0, required=True)
    abstentions = forms.IntegerField(min_value=0, required=True)
    absent = forms.IntegerField(min_value=0, required=True)

class ActiveDebateForm(forms.Form):
    def __init__(self, active_debate_choices, *args, **kwargs):
        super(ActiveDebateForm, self).__init__(*args, **kwargs)
        self.fields['active_debate'].choices = active_debate_choices

    session = forms.CharField(max_length=100, required=True)
    active_debate = forms.ChoiceField(choices=(), required=True)

class ActiveRoundForm(forms.Form):
    def __init__(self, active_round_choices, *args, **kwargs):
        super(ActiveRoundForm, self).__init__(*args, **kwargs)
        self.fields['active_round'].choices = active_round_choices

    session = forms.CharField(max_length=100, required=True)
    active_round = forms.ChoiceField(choices=(), required=True)
