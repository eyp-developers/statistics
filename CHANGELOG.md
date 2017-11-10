### 2017-11-10
* Improved the experience of creating a session with more detailed error messages.

### 2017-04-08
* We have added better error reporting, which will automatically send information about problems to us, should you encounter any.
* From now on, if you encounter an internal server error, you will be asked to describe what you did before the error happened.
* This will help us understand what led to the problem and allow us to fix it for you.

### 2017-02-28
* We optimised the code which produces the session pages to be more efficient and easier to maintain.
* This change did not alter the behaviour or features of GA Statistics, it soley improved the *behind the scenes* aspects of GA Statistics.


### 2017-02-25
* We *drastically* reduced the amount of database queries which were caused by loading the home page.
  * This should make it a little faster to load the home page, especially if there are more sessions in the database.
  * Facts for nerds
    * With the currently 122 sessions in our database, the amount of queries caused by loading the homepage was reduced from
    over 366 queries to a maximim of only a little more than 36 queries.
    * Without this optimisation, in the future, where more sessions are in the database, one query to the home page could have easily caused over a thousand queries to the database.
* We added a nicer message which explains where to add a new session in case the database contains no sessions at all.
  * This helps users who would like to [self-host](https://ga-statistics.readthedocs.io/en/latest/selfhosting/introduction.html) get started quicker
  * Self-hosting can be useful if you'd like to use GA Statistics at a venue without internet access.


### 2017-02-23
* Special characters will now be replaced by their non-special equivalents.
  * If you create a session named [Hódmezővásárhely](https://en.wikipedia.org/wiki/H%C3%B3dmez%C5%91v%C3%A1s%C3%A1rhely) the session's usernames will become hodmezovasarhely2017 and hodmezovasarhely2017_admin
  * This change makes it a lot easier for everyone on the team to log in, even if they lack the keyboard needed for these characters
  * Thanks to [@klarasch](https://github.com/eyp-developers/statistics/issues/137) for suggesting this [enhancement](https://github.com/eyp-developers/statistics/issues/137) on our project page on GitHub
  * If your session was created before this change, your session is not affected by this change and will keep its username including possible special characters.
* We added documentation on [how to create your own local copy of GA Statistics](https://ga-statistics.readthedocs.io/en/latest/selfhosting/docker.html) in case you do not have access to internet at your venue.

### 2017-02-21
* The home page now shows when exactly the last activity in an active session took place to reduce confusion as to whether the GA is actually happening in this instant or whether it was just active today at some earlier point
* Added the ability to show announcements on the home page
* Added the ability to show announcements on the create session page



### 2017-02-20
* We improved the [error page](https://stats.eyp.org/error), which now gives instructions on how to get help and generally looks nicer.


### 2017-02-03
* We fixed a bug which resulted in non-visible sessions showing up on the front-page as *currently going on* when points or votes were submitted to it.

### 2016-12-28
* We have introduced a new [documentation](http://ga-statistics.readthedocs.io/) in which you will find all sorts of handy knowledge about GA Statistics already now and even more in the future
* We added a link to the documentation to the navigation bar on all pages except debate-pages

### 2016-12-26
In the past, loading the front-page of GA Statistics for the first time took quite some time — especially using mobile networks. A front-page took an average 12MB to load with each session's picture weighing in at a little less than a MB.

This is now a thing of the past. 🎉

* The front-page now loads thumbnail versions of the session pictures
* The individual session and debate pages now load a high quality version of the session picture with reduced file-size

**Facts for nerds**
* Overall, the load time of the front-page on a 3G connection was reduced from 1.2 minutes to 9.75s
* Using a modern home WiFi connection, the front-page now loads in under three seconds at 2.17 seconds instead of the previous 12.82 seconds

### 2016-12-23
Since the beginning of GA Statistics, it was possible to upload images to give your session's page a personal touch and a connection to the city the session takes place in.

Recently, there has been a development towards uploading session's logos and reusing images intended to be used as Facebook header images. While of course, everyone is free to upload any image they think suits their session best, we would advise against following this trend, as those images do not play nicely with the websites layout in most cases.

Therefore, we'd like to ask you to stick to the new guidelines described below and on the *create session* page.

See for yourself. Which one would you prefer?

![back in the days](http://i.imgur.com/oCcrc18.jpg?1)

![currently](http://i.imgur.com/kb1Fah8.jpg?1)

* Clarify which kinds of images should be uploaded for sessions
  * Images should not contain text
  * Images should feature the city and ideally a well-known landmark the city is known for
  * Images should especially *not* be the session's logo or Facebook header image
* A new option has been added to allow you to credit the photographer
* A new option has been added to allow you to specify under which license the image has published
* We strongly recommend, that you use those new options, as it will ensure you will not get into legal trouble
* Add a background colour to the session-tiles on the front-page, which is shown before the images load

### 2016-12-12
* Clarify when the label `[Session]'s GA hasn't started yet` appears and how to hide it
* This additional information will only be shown to logged in users

### 2016-12-11
* Introduced a public and easy to understand changelog, you are looking at it right now
* Introduced a new bug-reporting and feature request system, we encourage you to use it
* Added a link to the changelog to the footer
* Added a link to the new bug-reporting and feature request system to the footer
* The `Get started` link now shows up on any page when the user is not logged in



### 2016-12-06
Oliver and Tom met in London to work on GA Statistics for a night. These are the results.

* Added a completely new front-page design
* Fixed a bug, which caused session dates to drift backwards when saving something on the settings page
* When using a page which allows the board to add statistical points on behalf of any committee, the subtopics now indicate which committee they are about
* Work has been started on introducing a very cool looking feature related to maps and the front-page — stay tuned to see it in action
