#!/usr/bin/env python
# encoding: utf-8

from gevent import monkey, thread 
monkey.patch_all()

import logging
logger = logging.getLogger(__name__)
import json

from SocketServer import StreamRequestHandler, ThreadingMixIn, TCPServer

class MethodAlreadyRegisted(Exception):
    pass

class MethodNotRegistered(Exception):
    pass


class GeventMixIn(ThreadingMixIn):
    
    def process_request(self, request, client_address):

        thread.start_new_thread(self.process_request_thread,
                                    args=(request, client_address))

class Dispatcher(object):
    
    def __init__(self):
        self.funcs = {}

    def call(self, func_name, *args):
        
        try:
            f = self.funcs[func_name]
        except KeyError:
            raise MethodNotRegistered
        
        return f(*args)
    
    def register(self, f):
        if f.func_name in self.funcs:
            raise MethodAlreadyRegisted
        self.funcs[f.func_name] = f

dispatcher = Dispatcher()

class GjsonHandler(StreamRequestHandler):
   
    timeout = 30

    def handle(self):

        while True:
            data = self.rfile.readline()
            try:
                msg = json.loads(data)
                print msg
                msg['result'] = None
                msg['error'] = None

                if all(('params' in msg,
                        'method' in msg,
                        'id' in msg)):
                    try:
                        method = msg.pop('method')
                        result = dispatcher.call(method, *msg.pop("params"))
                        msg['result'] = result
                    except Exception as err:
                        msg['error'] = unicode(err)
                else:
                    err = "not valid msg %s" % msg
                    msg['error'] = err

                json.dump(msg, self.wfile)
            except Exception as err:
                logger.error(err, exc_info=True)
                break

class GeventServer(GeventMixIn, TCPServer): pass

def new_server(address, port=0):
    
    return GeventServer((address, port), GjsonHandler)
