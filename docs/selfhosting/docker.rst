Using Docker
============
One of the best ways to host GA Statistics locally, is to use Docker.
Once you have installed Docker, you will not have to worry about any kind of configuration.
It will just work as expected.

Prerequisites
-------------
First of all, you will need to install Docker.
This is quite straight-forward and all the instructions can be found on the Docker Website.

.. note::
  If you have a choice of different computers to use, I recommend using a Mac, as the installation of Docker is easiest and
  creating an offline hotspot for other users to use your local copy of GA Statistics is also very easy.

Docker Installation Instructions by platform
____________________________________________

* `macOS <https://docs.docker.com/docker-for-mac/install/>`_
* `Linux <https://docs.docker.com/engine/installation/#on-linux>`_

  * Also make sure to `install docker-compose <https://docs.docker.com/compose/install/>`_, as it is not installed automatically on Linux.

* `Windows <https://docs.docker.com/docker-for-windows/install/>`_

You don't need to know how Docker works to hose your own local copy of GA Statistics,
but if you are interested, you can check out the `Docker Documentation <https://docs.docker.com/>`_ to learn more.

Starting your own copy of GA Statistics
---------------------------------------
Now, that you are all set, it's time to get your own copy of GA Statistics up and running.

#. Create a folder in which you want to store GA Statistics data
#. Save the `installation file <https://raw.githubusercontent.com/eyp-developers/statistics/master/docker-compose.yml>`_ to this folder.
  * Tip: Right click the above link and choose :code:`Save as...` to save the file in perfect condition and correctly named.
#. Ensure, that the file you just saved is named :code:`docker-compose.yml`.
#. Open a new Terminal or command line and browse to the folder, in which you have saved :code:`docker-compose.yml`.
#. Run the command :code:`docker-compose up` and wait until the server is fully started up.
  * Note: This will download about 600MB of data. Do this at home and avoid using up your monthly mobile data plan accidentally.
#. Open a browser and browse to http://localhost/.
#. If everything is working, head to http://localhost/create_session/ to create your session.

Allowing other users to connect to your copy of GA Statistics
-------------------------------------------------------------
To allow others to connect to your local copy of GA Statistics, everyone will need to be on the same network.
This network does not have to have a connection to the internet.
In order to set up such a network, you could open a hotspot on your phone and connect everyone to it.
Another option is to find a WiFi router and let it open a WiFi network where you are, without connecting it to the Internet.
Everyone will still be able to access the other devices on the same network, even without internet.

To actually connect to the local copy of GA Statistics, you will need to find out what your local IP address is.

How to set up a hotspot
_______________________

.. note::
  The device which sets up the hotspot and the device which is hosting GA Statistics do *not* need to be the same.

* `macOS <http://www.imore.com/how-turn-your-macs-internet-connection-wifi-hotspot-internet-sharing>`_
* `Linux <http://ubuntuhandbook.org/index.php/2014/09/3-ways-create-wifi-hotspot-ubuntu/>`_
* `Windows 10 <http://lifehacker.com/turn-your-windows-10-computer-into-a-wi-fi-hotspot-1724762931>`_


How to find your local IP address
_________________________________

To let others connect to your copy of GA Statistics, you must find out at which local IP your device is reachable.

* `macOS <http://www.wikihow.com/Find-Your-IP-Address-on-a-Mac>`_
* `Linux <http://askubuntu.com/a/430855>`_
* `Windows 7, 8, 10 <https://www.groovypost.com/howto/microsoft/windows-7/find-your-local-ip-address-windows-7-cmd/>`_

Using the local copy of GA Statistics
-------------------------------------
After everyone has connected to your local hotspot, they must enter the local IP address of the computer which is hosting the local copy of GA Statistics in their browsers.

Congratulations, you are now running your own local copy of GA Statistics, which you can use at any venue, even without any internet.
