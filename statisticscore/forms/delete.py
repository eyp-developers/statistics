from django import forms

class DeleteDataForm(forms.Form):
    pk = forms.IntegerField(min_value=0, required=True)
