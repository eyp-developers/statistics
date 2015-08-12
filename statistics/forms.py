from django import forms

class PointForm(forms.Form):
    #The point form needs to be fed with special data, in the form of an array of subtopics.
    #To do this, we change the definition of the form to accept an extra argument, the array of subtopics.
    def __init__(self, subtopic_choices, *args, **kwargs):
        super(PointForm, self).__init__(*args, **kwargs)
        self.fields['subtopics'].choices = subtopic_choices

    #This is setting up the point types in the same way as they are set up in the models file
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )

    #These are the other arguments that the point form needs for a successfully submitted point.
    #Note that the choices of the point_type is the previously defined point types and that
    #the choices for the subtopics needs to be set up, but empty.
    session = forms.CharField(max_length=100, required=True)
    committee = forms.CharField(max_length=8, required=True)
    debate = forms.CharField(max_length=8, required=True)
    round_no = forms.IntegerField(min_value=0, required=True)
    point_type = forms.ChoiceField(choices=POINT_TYPES, required=True)
    subtopics = forms.MultipleChoiceField(choices=(), required=True)

class VoteForm(forms.Form):
    #The vote form is simpler, as there are no custom definitions required, just plain data.
    session = forms.CharField(max_length=100, required=True)
    committee = forms.CharField(max_length=8, required=True)
    debate = forms.CharField(max_length=8, required=True)
    in_favour = forms.IntegerField(min_value=0, required=True)
    against = forms.IntegerField(min_value=0, required=True)
    abstentions = forms.IntegerField(min_value=0, required=True)
    absent = forms.IntegerField(min_value=0, required=True)

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
