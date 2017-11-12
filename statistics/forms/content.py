from django import forms


class ContentForm(forms.Form):
    #The contentpoint form needs special point types, but except for that it's a pretty simple form.
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )

    session = forms.CharField(max_length=100, required=True)
    committee = forms.CharField(max_length=8, required=True)
    debate = forms.CharField(max_length=8, required=True)
    point_type = forms.ChoiceField(choices=POINT_TYPES, required=True)
    content = forms.CharField(required=True)

class ContentEditForm(forms.Form):
    #The contentpoint form needs special point types, but except for that it's a pretty simple form.
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )

    pk = forms.IntegerField(min_value=0, required=True)
    session = forms.IntegerField(min_value=0, required=True)
    committee = forms.CharField(max_length=8, required=True)
    debate = forms.CharField(max_length=8, required=True)
    point_type = forms.ChoiceField(choices=POINT_TYPES, required=True)
    content = forms.CharField(required=True)
