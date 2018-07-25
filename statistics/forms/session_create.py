from django import forms
from statistics import countries, session_types

from ..models import SESSION_NAME_LEN, SESSION_DESCRIPTION_LEN, SESSION_AUTHOR_LEN, SESSION_LICENCE_LEN

class SessionForm(forms.Form):

    name = forms.CharField(max_length=SESSION_NAME_LEN, required=True, help_text='Short Session Name - Preferably Place/Year', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Izmir 2015'}))
    description = forms.CharField(max_length=SESSION_DESCRIPTION_LEN, required=True, help_text='Full Session Name', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '78th International Session of the EYP'}))
    type = forms.ChoiceField(choices=session_types.SESSION_TYPES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john.smith@eyp.org'}))
    country = forms.ChoiceField(choices=countries.SESSION_COUNTRIES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    picture = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    picture_author = forms.CharField(max_length=SESSION_AUTHOR_LEN, required=False, help_text="Please credit your picture's author appropriately.", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}))
    picture_author_link = forms.URLField(required=False, help_text="Please link to your picture's author.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}))
    picture_license = forms.CharField(max_length=SESSION_LICENCE_LEN, required=False, help_text="If you are allowed to use the picture because of a license like e.g. CC-BY-X.0 you must provide it's name here.", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CC-BY-4.0'}))
    picture_license_link = forms.URLField(required=False, help_text="If you are allowed to use the picture because of a license like e.g. CC-BY-X.0 you must provide a link to it here.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://creativecommons.org/licenses/by/4.0/'}))


    start_date = forms.DateField(required=True, help_text="This is the first day for Delegates.", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': '2017-07-17'}))
    end_date = forms.DateField(required=True, help_text="This is the last day for Delegates.", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': '2017-07-26'}))

    website = forms.URLField(required=False, help_text="Please add your NC's website if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
    facebook = forms.URLField(required=False, help_text="Please add your NC's Facebook page if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
    twitter = forms.URLField(required=False, help_text="Please add your NC's Twitter account if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
    topic_overviews = forms.URLField(required=False, help_text="Add a link to your sessions topic overviews.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
    resolutions = forms.URLField(required=False, help_text="Add a link to an online version of your resolution booklet as soon as you can.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))

    #Setting up statistic types
    STATISTICS = 'S'
    CONTENT = 'C'
    JOINTFORM = 'JF'
    SPLITFORM = 'SF'
    RUNNINGORDER = 'R'
    RUNNINGCONTENT = 'RC'
    STATISTIC_TYPES = (
        (STATISTICS, 'Statistics Only'),
        (CONTENT, 'Point Content Only'),
        (JOINTFORM, 'Joint Form Statistics'),
        (SPLITFORM, 'Split Form Statistics'),
        (RUNNINGORDER, 'Running Order Statistics'),
        (RUNNINGCONTENT, 'Running Order Statistics with Point Content')
    )
    #Making the statistics type a selectable option
    statistics = forms.ChoiceField(choices=STATISTIC_TYPES, help_text='What kind of statistics you want to run at your session', required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    #Since the voting choice is not a checkbox per se, the input type will be a CharField instead
    voting_enabled = forms.CharField(max_length=5, required=True, help_text='Enables digital voting for your session', widget=forms.CheckboxInput(attrs={'checked': ''}))
    gender_statistics = forms.CharField(max_length=5, required=True, help_text='Lets you track the gender equality of your GA', widget=forms.CheckboxInput(attrs={'checked': ''}))

    number_female_participants = forms.IntegerField(min_value=0, required=False, help_text='If you are tracking the gender equality of your session, please add this value. You can also do this later. Only count Delegates.', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    number_male_participants = forms.IntegerField(min_value=0, required=False, help_text='If you are tracking the gender equality of your session, please add this value. You can also do this later. Only count Delegates.', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    number_other_participants = forms.IntegerField(min_value=0, required=False, help_text='If you are tracking the gender equality of your session, please add this value. You can also do this later. Only count Delegates.', widget=forms.NumberInput(attrs={'class': 'form-control'}))

    max_rounds = forms.IntegerField(min_value=1, max_value=10, help_text='The maximum number of rounds of open debate during your GA', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '4'}))

    admin_password = forms.CharField(help_text='The password used to alter session settings and manage GA Stats', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    submission_password = forms.CharField(help_text='The password used by Chairs, Journalists or Organisers to submit statistics', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
