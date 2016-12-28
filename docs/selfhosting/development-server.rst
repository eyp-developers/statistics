Using the development server
============================

Normally, you would use this method to set up a development environment for GA Statistics.
This means, you probably already know what you are doing, but if you're just getting into it and this is your first
time working with `Python <https://www.python.org/>`_, `Django <https://www.djangoproject.com/>`_ or both,
then these instructions will help you get up and running.

Installing Prerequisites
------------------------

Python
______
Most importantly, you will need to check if you have Python installed. Python is the programming language which is used for all the logic
in GA Statistics. The Django Framework is based on Python, so there's no way around it when working on GA Statistics.
Luckily, Python is one of the easiest programming languages to learn, so don't be afraid. If you already know some programming basics,
then understanding Python won't be an issue for you.

You can find instructions on installing Python on your system on `wiki.python.org <https://wiki.python.org/moin/BeginnersGuide/Download>`_.

pip
___

pip is a package manager for Python packages. We will use it to install the packages we need for GA Statistics.
Depending on how you installed Python, you might already have a copy of pip on your system.
If you run the command :code:`pip freeze` and you see some output, which looks like a list of packages, then you are already good to go.
If this doesn't work, then you will have to install pip.

You can check out pip's documentation on `how to install pip <https://pip.pypa.io/en/stable/installing/>`_.

git
___

If you want to actually contribute back some code changes, you will need to install `git <https://git-scm.com/>`_.
Git is a free and open source distributed version control system and we use it to collaborate on the code, which makes up GA Statistics.
We actually even use it to work together on this documentation.

You can find instructions for installing git in their `documentation <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.



Setting up the development environment
--------------------------------------
Now that you have installed pip, it is time to To run this web app locally, clone the repository, cd into it and execute the following commands.

:code:`pip install virtualenv`

:code:`virtualenv .`

:code:`source bin/activate`

:code:`pip install -r requirements.txt`

:code:`python manage.py migrate`

:code:`python manage.py createsuperuser`

:code:`python manage.py runserver`

Please note that this is only a development server which should never be used for production scenarios.

You can now login to the [admin area of your local development server](http://localhost:8000/admin/) and start creating sample content.
