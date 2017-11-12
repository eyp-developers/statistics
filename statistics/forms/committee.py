from django import forms


class CommitteeForm(forms.Form):
    pk = forms.IntegerField(required=False)
    name = forms.CharField(max_length=8)
    topic = forms.CharField(max_length=1000)
