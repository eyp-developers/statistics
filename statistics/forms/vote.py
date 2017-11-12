from django import forms


class VoteForm(forms.Form):
    #The vote form is simpler, as there are no custom definitions required, just plain data.
    session = forms.CharField(max_length=100, required=True)
    committee = forms.CharField(max_length=8, required=True)
    debate = forms.CharField(max_length=8, required=True)
    in_favour = forms.IntegerField(min_value=0, required=True)
    against = forms.IntegerField(min_value=0, required=True)
    abstentions = forms.IntegerField(min_value=0, required=True)
    absent = forms.IntegerField(min_value=0, required=True)

class VoteEditForm(forms.Form):
    #The vote form is simpler, as there are no custom definitions required, just plain data.
    pk = forms.IntegerField(min_value=0, required=True)
    session = forms.IntegerField(min_value=0, required=True)
    committee = forms.CharField(max_length=8, required=True)
    debate = forms.CharField(max_length=8, required=True)
    in_favour = forms.IntegerField(min_value=0, required=True)
    against = forms.IntegerField(min_value=0, required=True)
    abstentions = forms.IntegerField(min_value=0, required=True)
    absent = forms.IntegerField(min_value=0, required=True)
