#!/usr/bin/python
"""
Spring - simple push notification trigger

@author: carsten

based on pyapns
@see https://github.com/samuraisam/pyapns
"""

from SocketServer import TCPServer
from optparse import OptionParser
from pyapns import configure, provision
from pyapns.client import notify
import argparse
import logging
import os
import pyapns._json
import pyapns.server
import twisted.application.internet
import twisted.web


logging.basicConfig()
log = logging.getLogger('spring.logger')
log.setLevel(logging.DEBUG)

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json')


def init_twisted():
    """
    startup twisted service; alternative: manually start twistd
    $ twistd -r default web --class=pyapns.server.APNSServer --port=7077  #simple example
    """
    with open(os.path.abspath(config_file)) as f:
        config = pyapns._json.loads(f.read())
    
    application = twisted.application.service.Application("pyapns application")
    
    resource = twisted.web.resource.Resource()
    service = pyapns.server.APNSServer()
    
    # get automatic provisioning
    if 'autoprovision' in config:
        for app in config['autoprovision']:
            service.xmlrpc_provision(app['app_id'],
                                     app['cert'],
                                     app['environment'],
                                     app['timeout'])
    
    # get port from config or 7077
    if 'port' in config:
        port = config['port']
    else:
        port = 7077
    
    resource.putChild('', service)
    site = twisted.web.server.Site(resource)
    assert port > 0, "invalid port"
    assert site is not None, "no site"

    log.debug("port %s; site %s" % (port, site))
    server = TCPServer(port, site)
    assert server is not None, "no server"
    server.setServiceParent(application)

def request_feedback():
    if not pyapns.client.OPTIONS['CONFIGURED']:
        log.info('configuration on the fly')
        configure({'HOST': 'http://localhost:7077/'})
        with open(os.path.abspath(config_file)) as f:
            config = pyapns._json.loads(f.read())
            for app in config['autoprovision']:
                app_id = app['app_id']
                log.info("requesting feeback for %s" % app_id)
                pyapns.feedback(app_id, async=False, callback=got_feedback, errback=got_error)

def got_feedback(tuples):
    if not tuples:
        log.debug('no invalid tuples - great')
        return
    log.debug('## tokens not reached:')
    for t in tuples:
        log.debug('%s - %s' % (t[0], t[1]))
    
    
def got_error(error):
    log.error("## Error handler\n%s" % error)


def push(app_id, message=None, badge=0, sound=None, custom=None):
    # FIXME: init service and push merged in one function - bad!
    #init_twisted()
    log.warn('auto-init of service currently not realiable; use manual start!')
        
    with open(os.path.abspath(config_file)) as f:
        config = pyapns._json.loads(f.read())
    
    ## configure on the fly
    if not pyapns.client.OPTIONS['CONFIGURED']:
        log.info('configuration on the fly')
        configure({'HOST': 'http://localhost:7077/'})
        if 'autoprovision' in config:
            for app in config['autoprovision']:
                if app['app_id'] == app_id:
                    log.info('found configuration for %s' % app_id)
                    assert os.path.exists(app['cert']) is True, "no file found at %s" % app['cert']
                    provision(app['app_id'], open(app['cert']).read(), app['environment'])

    ## create notification
    notification = {'aps':{}}
    if message: 
        notification['aps'].update({'alert': message})
    if badge:
        notification['aps'].update({'badge': int(badge)})
    if sound:
        notification['aps'].update({'sound': sound})
    if custom:    
        for key in custom:
            notification.update({key:custom[key]})

    log.debug('[%s] %d token; notification:\n%s\n' % (app_id, len(config['tokens']), notification))
    
    # notifications = []
    # for token in config['tokens']:
    #     notifications.append(notification)
    notify(app_id, config['tokens'], notification, async=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='spring', description='Triggers iOS push notifications.')
    parser.add_argument('-a', '--alert', type=str, dest='alert', 
                        help='alert text')
    parser.add_argument('-b', '--badge', type=int, dest='badge', 
                        help='badge number; \'0\' if you want to clear the app\'s current badge')
    parser.add_argument('-s', '--sound', type=str, dest='sound', 
                        help='sound file')
#    parser.add_argument('-c', '--custom', type=dict, dest='custom', 
#                        help='custom key/value pairs')
    parser.add_argument('-i', '--id', dest='app_id', 
                        help='application ID, if you have multiple apps registered')
    parser.add_argument('-f', '--feedback', dest='feedback', action='store_true', help='feedback service')
    parser.set_defaults(feedback=False)
    parser.add_argument('--version', action='version', version='spring v1.0')
    args = parser.parse_args()

    ## app id is required
    if args.app_id is None and args.feedback is False:
        parser.error('must define target application')

    if args.feedback is True:
        request_feedback()
    else:
        ## add file extension to sound file if missing
        if args.sound and args.sound.find('.caf') == -1:
            args.sound += '.caf'

        ## TODO: handle custom key/value pairs (pickle, json, ...)
        push(args.app_id, args.alert, args.badge, args.sound, None)