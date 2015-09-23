#!/usr/bin/env python
# encoding: utf-8

"""
Simple and high performance JSON RPC v1.0 server
"""

from gevent import monkey, server
monkey.patch_all()

import logging
logger = logging.getLogger(__name__)
import cjson
import socket

class MethodAlreadyRegisted(Exception):
    pass

class MethodNotRegistered(Exception):
    pass

class Dispatcher(object):
    
    def __init__(self):
        self.funcs = {}

    def call(self, func_name, *args):
        try:
            f = self.funcs[func_name]
        except KeyError:
            raise MethodNotRegistered("func name:%s not registered" % func_name)
        
        return f(*args)
    
    def register(self, f):
        if f.func_name in self.funcs:
            raise MethodAlreadyRegisted("func name:%s already registered" % f.func_name)
        self.funcs[f.func_name] = f
    
    def __call__(self, sock, address):

        rfile = sock.makefile("rb", -1)
        while not sock.closed:
            try:
                data = rfile.readline()
                msg = cjson.decode(data)
                msg['result'] = None
                msg['error'] = None

                if all(('params' in msg,
                        'method' in msg,
                        'id' in msg)):
                    try:
                        method = msg.pop('method')
                        result = self.call(method, *msg.pop("params"))
                        msg['result'] = result
                    except Exception as err:
                        msg['error'] = unicode(err)
                else:
                    err = "not valid msg %s" % msg
                    msg['error'] = err

                sock.sendall(cjson.encode(msg))
            except cjson.DecodeError as err:
                logger.debug(err)
            except Exception as err:
                logger.error(err, exc_info=True)
                return
            except socket.error as err:
                logger.warn(err)
                return

def new_server(address, port, dispatcher, **kwargs):
    s = server.StreamServer((address, port), dispatcher, **kwargs)
    return s


if __name__ == '__main__':

    import os
    dispatcher = Dispatcher()
    def add(x):
        return x[0]+x[1]
    def data(size):
        return os.urandom(int(size)).encode('hex')
    
    dispatcher.register(add)
    dispatcher.register(data)
    rpc = new_server('127.0.0.1', 8080, dispatcher)
    rpc.serve_forever()
