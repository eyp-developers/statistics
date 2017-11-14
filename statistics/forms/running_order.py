from django import forms


class PredictForm(forms.Form):
    #We need to use the same custon data as in the PointForm
    def __init__(self, subtopic_choices, *args, **kwargs):
        super(PredictForm, self).__init__(*args, **kwargs)
        self.fields['next_subtopics'].choices = subtopic_choices

    next_subtopics = forms.MultipleChoiceField(choices=(), required=False)

class PredictEditForm(forms.Form):
    pk = forms.IntegerField(min_value=0, required=True)

class RunningOrderForm(forms.Form):
    by = forms.IntegerField(min_value=0, required=True)
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )
    point_type = forms.ChoiceField(choices=POINT_TYPES, required=True)
