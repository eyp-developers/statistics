from django import forms

from django.contrib.auth import get_user_model


class SessionForm(forms.Form):

    #The countries of the session need to be set up in the same way as the model.
    ALBANIA = 'AL'
    ARMENIA = 'AM'
    AUSTRIA = 'AT'
    AZERBAIJAN = 'AZ'
    BELARUS = 'BY'
    BELGIUM = 'BE'
    BOSNIA_AND_HERZEGOVINA = 'BA'
    CROATIA = 'HR'
    CYPRUS = 'CY'
    CZECH_REPUBLIC = 'CZ'
    DENMARK = 'DK'
    ESTONIA = 'EE'
    FINLAND = 'FI'
    FRANCE = 'FR'
    GEORGIA = 'GE'
    GERMANY = 'DE'
    GREECE = 'GR'
    HUNGARY = 'HU'
    IRELAND = 'IE'
    ITALY = 'IT'
    KOSOVO = 'XK'
    LATVIA = 'LV'
    LITHUANIA = 'LT'
    LUXEMBOURG = 'LU'
    NETHERLANDS = 'NL'
    NORWAY = 'NO'
    POLAND = 'PL'
    PORTUGAL = 'PT'
    ROMANIA = 'RO'
    RUSSIA = 'RU'
    SERBIA = 'RS'
    SLOVENIA = 'SI'
    SPAIN = 'ES'
    SWEDEN = 'SE'
    SWITZERLAND = 'CH'
    TURKEY = 'TR'
    UKRAINE = 'UA'
    UNITED_KINGDOM = 'GB'
    SESSION_COUNTRIES = (
        (ALBANIA, 'Albania'),
        (ARMENIA, 'Armenia'),
        (AUSTRIA, 'Austria'),
        (AZERBAIJAN, 'Azerbaijan'),
        (BELARUS, 'Belarus'),
        (BELGIUM, 'Belgium'),
        (BOSNIA_AND_HERZEGOVINA, 'Bosnia and Herzegovina'),
        (CROATIA, 'Croatia'),
        (CYPRUS, 'Cyprus'),
        (CZECH_REPUBLIC, 'Czech Republic'),
        (DENMARK, 'Denmark'),
        (ESTONIA, 'Estonia'),
        (FINLAND, 'Finland'),
        (FRANCE, 'France'),
        (GEORGIA, 'Georgia'),
        (GERMANY, 'Germany'),
        (GREECE, 'Greece'),
        (HUNGARY, 'Hungary'),
        (IRELAND, 'Ireland'),
        (ITALY, 'Italy'),
        (KOSOVO, 'Kosovo'),
        (LATVIA, 'Latvia'),
        (LITHUANIA, 'Lithuania'),
        (LUXEMBOURG, 'Luxembourg'),
        (NETHERLANDS, 'The Netherlands'),
        (NORWAY, 'Norway'),
        (POLAND, 'Poland'),
        (PORTUGAL, 'Portugal'),
        (ROMANIA, 'Romania'),
        (RUSSIA, 'Russia'),
        (SERBIA, 'Serbia'),
        (SLOVENIA, 'Slovenia'),
        (SPAIN, 'Spain'),
        (SWEDEN, 'Sweden'),
        (SWITZERLAND, 'Swizerland'),
        (TURKEY, 'Turkey'),
        (UKRAINE, 'Ukraine'),
        (UNITED_KINGDOM, 'The United Kingdom'),
    )

    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=200, required=True)
    email = forms.EmailField()
    country = forms.ChoiceField(choices=SESSION_COUNTRIES, required=True)
    picture = forms.URLField(required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)

    website = forms.URLField(required=False)
    facebook = forms.URLField(required=False)
    twitter = forms.URLField(required=False)

    #Setting up statistic types
    STATISTICS = 'S'
    CONTENT = 'C'
    JOINTFORM = 'JF'
    SPLITFORM = 'SF'
    NONE = 'N/A'
    STATISTIC_TYPES = (
        (STATISTICS, 'Statistics Only'),
        (CONTENT, 'Point Content Only'),
        (JOINTFORM, 'Joint Form Statistics'),
        (SPLITFORM, 'Split Form Statistics'),
        (NONE, 'No Statistics (Only Voting)')
    )
    #Making the statistics type a selectable option
    statistics = forms.ChoiceField(choices=STATISTIC_TYPES, required=True)

    #Since the voting choice is not a checkbox per se, the input type will be a CharField instead
    voting = forms.CharField(max_length=5, required=True)

    max_rounds = forms.IntegerField(min_value=1, max_value=10)

    color = forms.CharField(max_length=20, required=True)

    admin_password = forms.CharField()
    submit_password = forms.CharField()

class SessionEditForm(forms.Form):
        #The countries of the session need to be set up in the same way as the model.
        ALBANIA = 'AL'
        ARMENIA = 'AM'
        AUSTRIA = 'AT'
        AZERBAIJAN = 'AZ'
        BELARUS = 'BY'
        BELGIUM = 'BE'
        BOSNIA_AND_HERZEGOVINA = 'BA'
        CROATIA = 'HR'
        CYPRUS = 'CY'
        CZECH_REPUBLIC = 'CZ'
        DENMARK = 'DK'
        ESTONIA = 'EE'
        FINLAND = 'FI'
        FRANCE = 'FR'
        GEORGIA = 'GE'
        GERMANY = 'DE'
        GREECE = 'GR'
        HUNGARY = 'HU'
        IRELAND = 'IE'
        ITALY = 'IT'
        KOSOVO = 'XK'
        LATVIA = 'LV'
        LITHUANIA = 'LT'
        LUXEMBOURG = 'LU'
        NETHERLANDS = 'NL'
        NORWAY = 'NO'
        POLAND = 'PL'
        PORTUGAL = 'PT'
        ROMANIA = 'RO'
        RUSSIA = 'RU'
        SERBIA = 'RS'
        SLOVENIA = 'SI'
        SPAIN = 'ES'
        SWEDEN = 'SE'
        SWITZERLAND = 'CH'
        TURKEY = 'TR'
        UKRAINE = 'UA'
        UNITED_KINGDOM = 'GB'
        SESSION_COUNTRIES = (
            (ALBANIA, 'Albania'),
            (ARMENIA, 'Armenia'),
            (AUSTRIA, 'Austria'),
            (AZERBAIJAN, 'Azerbaijan'),
            (BELARUS, 'Belarus'),
            (BELGIUM, 'Belgium'),
            (BOSNIA_AND_HERZEGOVINA, 'Bosnia and Herzegovina'),
            (CROATIA, 'Croatia'),
            (CYPRUS, 'Cyprus'),
            (CZECH_REPUBLIC, 'Czech Republic'),
            (DENMARK, 'Denmark'),
            (ESTONIA, 'Estonia'),
            (FINLAND, 'Finland'),
            (FRANCE, 'France'),
            (GEORGIA, 'Georgia'),
            (GERMANY, 'Germany'),
            (GREECE, 'Greece'),
            (HUNGARY, 'Hungary'),
            (IRELAND, 'Ireland'),
            (ITALY, 'Italy'),
            (KOSOVO, 'Kosovo'),
            (LATVIA, 'Latvia'),
            (LITHUANIA, 'Lithuania'),
            (LUXEMBOURG, 'Luxembourg'),
            (NETHERLANDS, 'The Netherlands'),
            (NORWAY, 'Norway'),
            (POLAND, 'Poland'),
            (PORTUGAL, 'Portugal'),
            (ROMANIA, 'Romania'),
            (RUSSIA, 'Russia'),
            (SERBIA, 'Serbia'),
            (SLOVENIA, 'Slovenia'),
            (SPAIN, 'Spain'),
            (SWEDEN, 'Sweden'),
            (SWITZERLAND, 'Swizerland'),
            (TURKEY, 'Turkey'),
            (UKRAINE, 'Ukraine'),
            (UNITED_KINGDOM, 'The United Kingdom'),
        )

        name = forms.CharField(max_length=100, required=True)
        description = forms.CharField(max_length=200, required=True)
        email = forms.EmailField()
        country = forms.ChoiceField(choices=SESSION_COUNTRIES, required=True)
        picture = forms.URLField(required=True)
        start_date = forms.DateField(required=True)
        end_date = forms.DateField(required=True)

        website = forms.URLField(required=False)
        facebook = forms.URLField(required=False)
        twitter = forms.URLField(required=False)
        resolution = forms.URLField(required=False)

        #Setting up statistic types
        STATISTICS = 'S'
        CONTENT = 'C'
        JOINTFORM = 'JF'
        SPLITFORM = 'SF'
        NONE = 'N/A'
        STATISTIC_TYPES = (
            (STATISTICS, 'Statistics Only'),
            (CONTENT, 'Point Content Only'),
            (JOINTFORM, 'Joint Form Statistics'),
            (SPLITFORM, 'Split Form Statistics'),
            (NONE, 'No Statistics (Only Voting)')
        )
        #Making the statistics type a selectable option
        statistics = forms.ChoiceField(choices=STATISTIC_TYPES, required=True)

        #Since the voting choice is not a checkbox per se, the input type will be a CharField instead
        voting = forms.BooleanField(required=False)

        max_rounds = forms.IntegerField(min_value=1, max_value=10)

        RED = 'red'
        PINK = 'pink'
        PURPLE = 'purple'
        DEEP_PURPLE = 'deep-purple'
        INDIGO = 'indigo'
        BLUE = 'blue'
        LIGHT_BLUE = 'light-blue'
        CYAN = 'cyan'
        TEAL = 'teal'
        GREEN = 'green'
        LIGHT_GREEN = 'light-green'
        LIME = 'lime'
        YELLOW = 'yellow'
        AMBER = 'amber'
        ORANGE = 'orange'
        DEEP_ORANGE = 'deep-orange'
        BLUE_GREY = 'blue-grey'
        COLOR_TYPES = (
            (RED, 'Red'),
            (PINK, 'Pink'),
            (PURPLE, 'Purple'),
            (DEEP_PURPLE, 'Deep Purple'),
            (INDIGO, 'Indigo'),
            (BLUE, 'Blue'),
            (LIGHT_BLUE, 'Light Blue'),
            (CYAN, 'Cyan'),
            (TEAL, 'Teal'),
            (GREEN, 'Green'),
            (LIGHT_GREEN, 'Light Green'),
            (LIME, 'Lime'),
            (YELLOW, 'Yellow'),
            (AMBER, 'Amber'),
            (ORANGE, 'Orange'),
            (DEEP_ORANGE, 'Deep Orange'),
            (BLUE_GREY, 'Blue Grey'),
        )
        color = forms.ChoiceField(choices=COLOR_TYPES, required=True)

        is_visible = forms.BooleanField(required=False)

        technical_problems = forms.BooleanField(required=False)

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

User = get_user_model()

class LoginForm(forms.Form):
    # This is the form a user fills out to log in
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
