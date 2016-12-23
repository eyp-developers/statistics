from django import forms

from django.contrib.auth import get_user_model
from statistics import countries, session_types

class SessionForm(forms.Form):

    name = forms.CharField(max_length=100, required=True, help_text='Short Session Name - Preferably Place/Year', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Izmir 2015'}))
    description = forms.CharField(max_length=200, required=True, help_text='Full Session Name', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '78th International Session of the EYP'}))
    type = forms.ChoiceField(choices=session_types.SESSION_TYPES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john.smith@eyp.org'}))
    country = forms.ChoiceField(choices=countries.SESSION_COUNTRIES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    picture = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    picture_author = forms.CharField(required=False, help_text="Please credit your picture's author appropriately.", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}))
    picture_author_link = forms.URLField(required=False, help_text="Please link to your picture's author.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}))
    picture_license = forms.CharField(required=False, help_text="If you are allowed to use the picture because of a license like e.g. CC-BY-X.0 you must provide it's name here.", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CC-BY-4.0'}))
    picture_license_link = forms.URLField(required=False, help_text="If you are allowed to use the picture because of a license like e.g. CC-BY-X.0 you must provide a link to it here.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://creativecommons.org/licenses/by/4.0/'}))


    start_date = forms.DateField(required=True, help_text="This is the first day for Delegates.", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': '2017-07-17'}))
    end_date = forms.DateField(required=True, help_text="This is the last day for Delegates.", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': '2017-07-26'}))

    website = forms.URLField(required=False, help_text="Please add your NC's website if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
    facebook = forms.URLField(required=False, help_text="Please add your NC's Facebook page if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
    twitter = forms.URLField(required=False, help_text="Please add your NC's Twitter account if you do not have one for your event.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))
    resolution = forms.URLField(required=False, help_text="Please add a link to an online version of your resolution booklet as soon as you can.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))

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

    #Was used to chose the session color - no longer used as everything is blue.
    #color = forms.CharField(max_length=20, required=True)

    admin_password = forms.CharField(help_text='The password used to alter session settings and manage GA Stats', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    submission_password = forms.CharField(help_text='The password used by Chairs, Journalists or Organisers to submit statistics', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

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
        resolution = forms.URLField(required=False, help_text="Please add a link to an online version of your resolution booklet as soon as you can.", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional ...'}))

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

class CommitteeForm(forms.Form):

    pk = forms.IntegerField(required=False)
    name = forms.CharField(max_length=8)
    topic = forms.CharField(max_length=1000)

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

class PointEditForm(forms.Form):
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
    pk = forms.IntegerField(min_value=0, required=True)
    session = forms.IntegerField(min_value=0, required=True)
    committee = forms.CharField(max_length=8, required=True)
    debate = forms.CharField(max_length=8, required=True)
    round_no = forms.IntegerField(min_value=0, required=True)
    point_type = forms.ChoiceField(choices=POINT_TYPES, required=True)

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

class DeleteDataForm(forms.Form):
    pk = forms.IntegerField(min_value=0, required=True)

User = get_user_model() # This belongs to the Login Form

class LoginForm(forms.Form):
    # This is the form a user fills out to log in
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
