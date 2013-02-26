spring
======

Sends remote push notifications to registered devices. Build for local debug and development. Currently only iOS push notifications supported.


Installation
------------
1. get [Python](http://www.python.org/) (most Unix-like OS' come with python pre-installed)
1. [pyapns](https://github.com/samuraisam/pyapns) (Apple push notification handler)

    $ pip install pyapns
1. [twisted](http://twistedmatrix.com/trac/) (required by pyapns)

    $ pip install twisted
1. [pyOpenSSL](https://pypi.python.org/pypi/pyOpenSSL) (required by pyapns)

    $ pip install pyOpenSSL
    
1. start twistd service; example:

	$ twistd -r default web --class=pyapns.server.APNSServer --port=7077
	
1. run the script; example:

	$ ./spring.py -a 'hello spring!' -b 42 -s default -i 'sandbox:my_awesome_app'