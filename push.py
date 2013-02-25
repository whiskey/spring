#!/usr/bin/python
'''
Spring - simple push notification trigger

@author: carsten

based on pyapns
@see https://github.com/samuraisam/pyapns
'''

from optparse import OptionParser
from pyapns import configure, provision
import os
import pyapns._json
import pyapns.server
import twisted.application.internet
import twisted.web

from pyapns.client import notify
from SocketServer import TCPServer

import logging

logging.basicConfig()
log = logging.getLogger('spring.logger')
log.setLevel(logging.DEBUG)

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json')

def init_twisted():
    '''
    startup twisted service; alternative: manually start twistd
    $ twistd -r default web --class=pyapns.server.APNSServer --port=7077  #simple example
    '''
    with open(os.path.abspath(config_file)) as f:
        config = pyapns._json.loads(f.read())
    
    application = twisted.application.service.Application("pyapns application")
    
    resource = twisted.web.resource.Resource()
    service = pyapns.server.APNSServer()
    
    # get automatic provisioning
    if 'autoprovision' in config:
        for app in config['autoprovision']:
            service.xmlrpc_provision(app['app_id'], app['cert'], app['environment'], 
                                     app['timeout'])
    
    # get port from config or 7077
    if 'port' in config:
        port = config['port']
    else:
        port = 7077
    
    resource.putChild('', service)
    site = twisted.web.server.Site(resource)
    
    ## FIXME: currently broken 
    ##server = TCPServer(port, site)
    ##server.setServiceParent(application)
    
    print '''#######################
    Auto-launch of twisted currently not implemented!
    Please start twisted instance manually: 
    $ twistd -r default web --class=pyapns.server.APNSServer --port=7077  #simple example
#######################'''

def got_feedback(tuples):
    if not tuples: return
    log.debug('## tokens not reached:')
    for t in tuples:
        log.debug('%s - %s' % (t[0],t[1]))
    
def got_error(error):
    log.error('## Error handler')
    log.error(error)

def push(app_id, message=None, badge=0, sound=None, custom=None):
    # FIXME: init and push merged in one function - bad!
    #init_twisted() # under construction
    
    with open(os.path.abspath(config_file)) as f:
        config = pyapns._json.loads(f.read())
    
    ####
    configure({'HOST': 'http://localhost:7077/'})
    if 'autoprovision' in config:
        for app in config['autoprovision']:
            log.debug('[%(id)s] cert: %(cert)s (%(env)s)' % {'id': app['app_id'],
                                                             'cert': app['cert'],
                                                             'env': app['environment']})
            if os.path.exists(app['cert']):
                provision(app['app_id'], open(app['cert']).read(), app['environment'])
            else:
                log.error('no file at %s found!' % app['cert'])
    ####
    pyapns.feedback(app_id, async=True, callback=got_feedback, errback=got_error)
    
    ## create notification
    notification = {'aps':{}}
    if message: 
        notification['aps'].update({'alert': message})
    if badge:
        notification['aps'].update({'badge': int(badge)})
    if sound:
        notification['aps'].update({'sound':sound})
    if custom:    
        for key in custom:
            notification.update({key:custom[key]})
    log.debug('[%s] %d token; notification:\n%s\n' % (app_id, len(config['tokens']), notification))
    
    notifications = []
    for token in config['tokens']:
        notifications.append(notification)
    notify(app_id, config['tokens'], notifications, async=True)


if __name__ == '__main__':
    parser = OptionParser(version='spring v1.0')
    parser.add_option('-a', '--alert', dest='alert', help='alert text')
    parser.add_option('-b', '--badge', dest='badge', help='badge number; \'0\' if you want to clear the app\'s current badge')
    parser.add_option('-s', '--sound', dest='sound', help='sound file')
    parser.add_option('-c', '--custom', dest='custom', help='custom key/value pairs')
    ## handle arguments
    (options, args) = parser.parse_args()
    if len(args) == 4:
        options.alert = args[0]
        options.badge = args[1]
        options.sound = args[2]
        options.custom = args[3]
    elif len(args) == 3:
        options.alert = args[0]
        options.badge = args[1]
        options.sound = args[2]
    elif len(args) == 2:
        options.alert = args[0]
        options.badge = args[1]
    elif len(args) == 1:
        options.alert = args[0]
    else:
        parser.error("incorrect number of arguments")
        
    ## add file extension to sound file if missing
    if options.sound and options.sound.find('.caf') == -1:
        options.sound += '.caf'
        
    ## TODO: get app id
    push('production:grepolite', options.alert, options.badge, options.sound, options.custom)