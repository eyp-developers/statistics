# statistics [![Build Status](https://travis-ci.org/eyp-developers/statistics.svg?branch=master)](https://travis-ci.org/eyp-developers/statistics) [![Documentation Status](http://readthedocs.org/projects/ga-statistics/badge/?version=latest)](http://ga-statistics.readthedocs.io/en/latest/?badge=latest) [![Selected for development](https://badge.waffle.io/eyp-developers/statistics.svg?label=selected&title=Selected for Development)](http://waffle.io/eyp-developers/statistics) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/7825905562154948a00906e36e202efd/badge.svg)](https://www.quantifiedcode.com/app/project/7825905562154948a00906e36e202efd)

Catering all the statistics lovers of the European Youth Parliament

***
Welcome! We aim to provide a GA Statistics platform, which can be used on any given session with any set of committees or statistics requirements. It's completely open source and is built using [Python](http://python.org) in conjunction with the [Django Web Framework](https://www.djangoproject.com/).

***
![example image ga statistics](http://i.imgur.com/DM6zeJS.jpg)

***

## Is `statistics` ready to be used?

Yes, you can now use it for your own session. Alternatively, you can help to improve it if you like! Submit ideas as issues or contact us for cooperation opportunities. We also consider well coded, documented, tested and meaningful pull requests.

## What does it look like at the moment?

You can have a look yourself. At the moment, the project is available at [stats.eyp.org](https://stats.eyp.org).

## How can I use `statistics` during my session?

At the moment, you are able to add your session by visiting [stats.eyp.org/create_session/](https://stats.eyp.org/create_session/).

## How can I run a local copy of `statistics`?

To run this web app locally, clone the repository, cd into it and execute the following commands.

`pip install virtualenv`

`virtualenv .`

`source bin/activate`

`pip install -r requirements.txt`

`python manage.py migrate`

`python manage.py createsuperuser`

`python manage.py runserver`

Please note that this is only a development server which should never be used for production scenarios.

You can now login to the [admin area of your local development server](http://localhost:8000/admin/) and start creating sample content.

### Troubleshooting

If you run into problems try installing the dependencies from `requirements.txt` using `pip install -r requirements.txt` but be aware whether you're in a virtual environment or not. We do not want to alter the system's actual environment.


## I would like to have a new feature!

Please feel free to share your ideas! We'd love to hear them! Just add them to the issues of the project. You can also inquire about becoming a member of EYP Developers by contacting any of the projects maintainers.


## How can I help to help make `statistics` better?
You can of course send pull requests which contain features. Please make sure to contact us first to make sure that we can accept your feature into the master repository.

## I don't know how I got here, what is all of this?

If you don't know what the `EYP` (European Youth Parliament) is, read through our [Wikipedia Article](http://en.wikipedia.org/wiki/European_Youth_Parliament) or visit our [website](http://eyp.org).

Every time the people who are part of this organisation gather for a large event, a part of this event is called the `GA`. It stands for [General Assembly](http://en.wikipedia.org/wiki/General_assembly) and it's exactly that. During the `GA` the participants will discuss different topics in various manners. We designed `statistics` to keep track of all of this data and make it nice and easy to collect and display it.
