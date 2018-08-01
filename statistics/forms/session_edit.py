from django import forms
from statistics import countries, session_types


class SessionEditForm(forms.Form):

        name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
        description = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs=({'class': 'form-control'})))
        type = forms.ChoiceField(choices=session_types.SESSION_TYPES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
        email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
        country = forms.ChoiceField(choices=countries.SESSION_COUNTRIES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))

        picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
        picture_author = forms.CharField(required=False, help_text="Please credit your picture's author appropriately.", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}))
        picture_author_link = forms.URLField(required=False, help_text="Please link to your picture's author.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}))
        picture_license = forms.CharField(required=False, help_text="If you are allowed to use the picture because of a license like e.g. CC-BY-X.0 you must provide it's name here.", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CC-BY-4.0'}))
        picture_license_link = forms.URLField(required=False, help_text="If you are allowed to use the picture because of a license like e.g. CC-BY-X.0 you must provide a link to it here.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://creativecommons.org/licenses/by/4.0/'}))

        start_date = forms.DateField(required=True, help_text="This is the first day for Delegates.", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': '2017-07-17'}))
        end_date = forms.DateField(required=True, help_text="This is the last day for Delegates.", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': '2017-07-26'}))

        website = forms.URLField(required=False, help_text="Please add your NC's website if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
        facebook = forms.URLField(required=False, help_text="Please add your NC's Facebook page if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
        twitter = forms.URLField(required=False, help_text="Please add your NC's Twitter account if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
        topic_overviews = forms.URLField(required=False, help_text="Add a link to your sessions topic overviews.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
        resolutions = forms.URLField(required=False, help_text="Please add a link to an online version of your resolution booklet as soon as you can.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))

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
        statistics = forms.ChoiceField(choices=STATISTIC_TYPES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))

        #Since the voting choice is not a checkbox per se, the input type will be a CharField instead
        voting_enabled = forms.CharField(max_length=5, required=False, widget=forms.CheckboxInput())
        gender_statistics = forms.CharField(max_length=5, required=False, widget=forms.CheckboxInput())

        number_female_participants = forms.IntegerField(min_value=0, required=False, help_text='If you are tracking the gender equality of your session, please add this value. You can also do this later. Only count Delegates.', widget=forms.NumberInput(attrs={'class': 'form-control'}))
        number_male_participants = forms.IntegerField(min_value=0, required=False, help_text='If you are tracking the gender equality of your session, please add this value. You can also do this later. Only count Delegates.', widget=forms.NumberInput(attrs={'class': 'form-control'}))
        number_other_participants = forms.IntegerField(min_value=0, required=False, help_text='If you are tracking the gender equality of your session, please add this value. You can also do this later. Only count Delegates.', widget=forms.NumberInput(attrs={'class': 'form-control'}))


        max_rounds = forms.IntegerField(min_value=1, max_value=10, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '4'}))

        is_visible = forms.BooleanField(required=False, widget=forms.CheckboxInput())

        technical_problems = forms.BooleanField(required=False, widget=forms.CheckboxInput())
