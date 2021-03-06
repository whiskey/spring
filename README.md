spring
======

Sends remote push notifications to registered devices. Build for local debug and development. Currently only iOS push notifications supported.


Installation
------------
1. get [Python](http://www.python.org/) (most Unix-like OS' come with python pre-installed)

1. [pyapns](https://github.com/samuraisam/pyapns) (Apple push notification handler)

	`$ pip install pyapns`

1. [twisted](http://twistedmatrix.com/trac/) (required by pyapns)

    `$ pip install twisted`
    
1. [pyOpenSSL](https://pypi.python.org/pypi/pyOpenSSL) (required by pyapns)

    `$ pip install pyOpenSSL`
    
1. [] (strongly recommended by pyOpenSSL)

	`$ pip install service_identity`
 
   
1. if you need to convert your export of the push certificate and private key to a .pem file use

    `$ openssl pkcs12 -in certs.p12 -out certs.pem -nodes`

1. copy the `config.json.example` file to `config.json` and adjust to your settings

1. start twistd service; example:

	`$ twistd -r default web --class=pyapns.server.APNSServer --port=7077`
	
1. run the script; example:

	`$ ./spring.py -a 'hello spring!' -b 42 -s default -i 'sandbox:my_awesome_app'`
