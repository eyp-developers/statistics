Using the development server
============================

Normally, you would use this method to set up a development environment for GA Statistics.
This means, you probably already know what you are doing, but if you're just getting into it and this is your first
time working with `Python <https://www.python.org/>`_, `Django <https://www.djangoproject.com/>`_ or both,
then these instructions will help you get up and running.

Prerequisites
-------------

Installing Python
_________________
Most importantly, you will need to check if you have Python installed. Python is the programming language which is used for all the logic
in GA Statistics. The Django Framework is based on Python, so there's no way around it when working on GA Statistics.
Luckily, Python is one of the easiest programming languages to learn, so don't be afraid. If you already know some programming basics,
then understanding Python won't be an issue for you.

You can find instructions on installing Python on your system on `wiki.python.org <https://wiki.python.org/moin/BeginnersGuide/Download>`_.

Installing pip
______________

pip is a package manager for Python packages. We will use it to install the packages we need for GA Statistics.
Depending on how you installed Python, you might already have a copy of pip on your system.
If you run the command :code:`pip freeze` and you see some output, which looks like a list of packages, then you are already good to go.
If this doesn't work, then you will have to install pip.

You can check out pip's documentation on `how to install pip <https://pip.pypa.io/en/stable/installing/>`_.

Installing git
______________

If you want to actually contribute back some code changes, you will need to install `git <https://git-scm.com/>`_.
Git is a free and open source distributed version control system and we use it to collaborate on the code, which makes up GA Statistics.
We actually even use it to work together on this documentation.

You can find instructions for installing git in their `documentation <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.

Cloning the repo
________________

Doing what? Cloning the repo(sitory) could be translated as `downloading GA Statistics' code`.
To do that, you will use git, which you should now have on your computer.

To clone the repository from GitHub, run the following command.

:code:`git clone https://github.com/eyp-developers/statistics.git`

You will now find a copy of GA Statistics in a folder called `statistics`. To change into the directory, run the following command.

:code:`cd statistics`

Setting up the development environment
--------------------------------------

If you have followed the above steps, you are now ready to set up the development environment. These steps assume, that you are inside of the statistics folder.

First, we want to install a tool called `virtualenv <https://virtualenv.pypa.io/en/stable/>`_. It allows us to install python packages into a virtual environment.
This ensures, that no other packages or older versions of packages get in our way and break things.

:code:`pip install virtualenv`

Now, you create a new virtual environment in the local directory, as indicated by the :code:`.`, which refers to your current location.

:code:`virtualenv .`

Now, you will have to activate the virtual environment by sourcing the script located in :code:`bin/activate`.

:code:`source bin/activate`

Now, you are going to install the required python packages for running a local copy of GA Statistics.
These will only be available while you are in the virtual environment, which you can enter by running the above command.

:code:`pip install -r requirements.txt`

Alright, we are almost done. You are now ready to run Django, but first, we need to initialise the database.
At the moment, it is completely empty and running GA Statistics would lead to errors. The next command will do this for us.

:code:`python manage.py migrate`

You would probably like to have admin access, so you should create a super user.
You can manage any session with this user and also access the administration backend.

:code:`python manage.py createsuperuser`

This is it, this is the final moment. If everything went alright, then you are now able to run your local copy of GA Statistics.

:code:`python manage.py runserver`

Please note that this is only a development server which should never be used for production scenarios.

You can now login to the `admin area of your local development server <http://localhost:8000/admin/>`_ and start using your local copy of GA Statistics.
If you'd like to create a session, you can do so `here <http://localhost:8000/create_session/>`_.
