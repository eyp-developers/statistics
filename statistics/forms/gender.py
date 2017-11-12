from django import forms

class GenderForm(forms.Form):
    def __init__(self, committee_choices, *args, **kwargs):
        super(GenderForm, self).__init__(*args, **kwargs)
        self.fields['committee'].choices = committee_choices

    committee = forms.ChoiceField(choices=(), required=True)

    FEMALE = 'F'
    MALE = 'M'
    OTHER = 'O'
    GENDERS = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
        (OTHER, 'Other')
    )

    gender = forms.ChoiceField(choices=GENDERS, required=True)
