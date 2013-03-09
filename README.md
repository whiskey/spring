spring
======

Sends remote push notifications to registered devices. Build for local debug and development. Currently only iOS push notifications supported.


Installation
------------
1. get [Python](http://www.python.org/) (most Unix-like OS' come with python pre-installed)

1. [pyapns](https://github.com/samuraisam/pyapns) (Apple push notification handler)

1. if you don't have pip installed, get it via easy_install
	$ sudo easy_install pip

    $ sudo pip install pyapns
1. [twisted](http://twistedmatrix.com/trac/) (required by pyapns)

    $ sudo pip install twisted
1. [pyOpenSSL](https://pypi.python.org/pypi/pyOpenSSL) (required by pyapns)

    $ sudo pip install pyOpenSSL
    
1. copy the _config.json.example_ file to _config.json_ and adjust to your settings
    
1. start twistd service; example:

	$ twistd -r default web --class=pyapns.server.APNSServer --port=7077
	
1. run the script; example:

	$ ./spring.py -a 'hello spring!' -b 42 -s default -i 'sandbox:my_awesome_app'
