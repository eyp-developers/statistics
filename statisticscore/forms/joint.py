from django import forms


class JointForm(forms.Form):
    #The point form needs to be fed with special data, in the form of an array of subtopics.
    #To do this, we change the definition of the form to accept an extra argument, the array of subtopics.
    def __init__(self, subtopic_choices, *args, **kwargs):
        super(JointForm, self).__init__(*args, **kwargs)
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
    content = forms.CharField(required=True)
