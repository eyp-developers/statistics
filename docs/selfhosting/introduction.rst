Introduction
============

You have a few options when it comes to running GA Statistics on your own computer.
But before you go ahead and do host GA Statistics on your own computer, you should ask yourself, why you would like to do that.

Why?
----

Normally, if you wanted to to use GA Statistics, you would do so by going to `our website <https://stats.eyp.org/create_session/>`_ and setting up your session there.
If that sounds like what you want to do, then great! Feel free to go ahead and start using GA Statistics on our server, that's why we put it there.

If you're still with me, then this is probably not an option. So why would you like to run GA Statistics locally?
Depending on your scenario, different approaches to hosting locally are recommended.

.. note::
  Of course, all of these approaches allow you to host a local copy of GA Statistics in the same manner,
  so the difference lies in how easy it is
  to set up and whether you need the extra complexity to achieve your goal.

Lack of good internet
---------------------
The most common reason to host your own local instance of GA Statistics would be to *circumvent the requirement of having an internet connection* in your GA venue.
While we hope, that we will soon live in a world, where a reliable internet connection is available everywhere,
we are painfully aware that this is *especially* not the case in your usual GA venue.

The easiest way to set up a local instance of GA Statistics is :doc:`using Docker <docker>`.

Prerequisites
_____________

* Bad internet
   - If your internet is good, you should simply sign up on https://stats.eyp.org/create_session/ and use the already available platform
* A device, capable of opening up a WiFi hotspot
   - Routers, Phones, every MacBook you have ever touched, probably most of the Windows Computers too, it's just a little harder
   - It is not important, whether you can access the internet through this device
   - It is important, that the devices connected to the hotspot can talk to each other internally on the same network
   - This is the case for any phone's hotspot for example, so it will probably just work, even if you do not know what any of this means
* A will to learn new things
   - When setting up GA Statistics for offline use, you will most likely do some things you have never done before
   - These things are not hard, but as with everything that is new, they might seem scary at first
   - There is no reason to be scared, meaning the next prerequisite should come naturally
* No fear of just trying and seeing if it works
   - Ideally not on the same day as the GA
   - Alternatively, you can take some computer nerd and let them handle it
   - Make sure to ask them nicely fist

Becoming a contributor
----------------------
Another humble, but of course less common, reason to run GA Statistics locally would be to become a contributor.
You will most likely want to run a :doc:`development server <development-server>`.
