Slick
=====

Slick is a reference implementation for using the `SoftLayer Python Bindings <https://github.com/softlayer/softlayer-api-python-client>`_. It implements a small web portal using a variety of open source projects to show the type of application you can build with the bindings.

.. WARNING::
   This software is currently in active development. Some expertise is required for initial installation and setup.

Installation
------------
#### Prerequirements
```bash
apt-get install libpq-dev postgresql python-pip git python-dev
```

#### DB Setup
I'm using postgresql, but you can use mysql if you like. Just change the bindings in alembic.ini and config.py
```bash
su postgresql
pgsql
create user slick with password 'slick1234';
create database slick owner slick;
```

#### Get everything running
If you used a better password than slick1234 make sure you change alembic.ini and config.py after you clone the repo

```bash
cd /usr/local/
git clone https://github.com/softlayer/slick.git
cd slick
python setup.py install
```
If setup.py failed to install, make sure you install any missing packages and try again before continuing.


This will setup the database
```bash
alembic upgrade head   
```

This will start the web server on port 5000
```bash
python run.py
```
Then just head over to http://<hostname>:5000 and you should be able to login with your SoftLayer portal username and password.
To run the server as a daemon just add the & symbol to the end of that command. There is currently no init script or anything fancy like that.

I'll leave seting up nginx as an excersize for the reader.


System Requirements
-------------------
* This library has been tested on Python 2.7 only. It may work on other versions.
* A valid SoftLayer API username and key are required to call SoftLayer's API

Copyright
---------
This software is Copyright (c) 2013 SoftLayer Technologies, Inc.
See the bundled LICENSE file for more information.
