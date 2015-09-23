#!/usr/bin/env python
# encoding: utf-8

"""
Simple and yet high performance JSON RPC v1.0 server/client
"""

from gevent import monkey, server, socket as gsocket
monkey.patch_all()

import logging
logger = logging.getLogger(__name__)
import cjson
import socket

class RPCException(Exception): pass
class MethodAlreadyRegisted(RPCException): pass
class MethodNotRegistered(RPCException): pass

class Dispatcher(object):
    
    def __init__(self):
        self.funcs = {}

    def call(self, func_name, *args):
        try:
            f = self.funcs[func_name]
        except KeyError:
            raise MethodNotRegistered("func name:%s not registered" % func_name)
        
        return f(*args)
    
    def register(self, f, name=None):
        
        if not callable(f):
            raise TypeError("%s is not callable object", f)

        if not name:
            name = f.__name__

        if name in self.funcs:
            raise MethodAlreadyRegisted("func name:%s already registered" % name)
        logger.info("register func: %s", name)
        self.funcs[name] = f

    def register_module(self, module_name):
        import importlib
        m = importlib.import_module(module_name)
        for k, v in m.__dict__.items():
            if not k.startswith("_") and callable(v):
                self.register(v, module_name +'.'+ k) 
    
    def __call__(self, sock, address):

        rfile = sock.makefile("rb", -1)
        logger.debug("new connection %s", address)

        while not sock.closed:
            try:
                data = rfile.readline()
                if len(data) == 0:
                    logger.info("connection %s closed", address)
                    break
                logger.debug('read %d from %s', len(data), address)
            except socket.error as err:
                logger.warn(err)
                return

            try:
                msg = cjson.decode(data)
                if not isinstance(msg, dict):
                    logger.warn("not valid rpc request %s", msg)
                    continue
            except cjson.DecodeError as err:
                logger.debug(err)
                return

            msg['result'] = None
            msg['error'] = None

            if ('params' in msg and
                'method' in msg and
                    'id' in msg ):
                try:
                    method = msg.pop('method')
                    result = self.call(method, *msg.pop("params"))
                    msg['result'] = result
                except Exception as err:
                    logger.error(err, exc_info=True)
                    msg['error'] = u"%s %s " % (err.__class__.__name__, err.message)

            else:
                err = "not valid msg %s" % msg
                msg['error'] = err

            sock.sendall(cjson.encode(msg)+'\n')

default_dispatcher = Dispatcher()
register = default_dispatcher.register
register_module = default_dispatcher.register_module

class Client(object):
    """
    Client 
    """
    def __init__(self, dest):
        """
        :params dest:
        """
        self.dest = dest
        self.sock = gsocket.socket()
        self.rfile = self.sock.makefile("rb", -1)
        self.sock.connect(dest)
        self.id = 0

    def __call__(self, method, *args):
        self.id += 1
        msg = dict(method=method,
                   id=self.id,
                   params=args)

        self.sock.send(cjson.encode(msg)+'\n')
        rsp = cjson.decode(self.rfile.readline())

        if rsp['error']:
            raise RPCException(rsp['error'])
        
        return rsp['result']

def new_server(dispatcher, address, port, **kwargs):
    """
    :params dispatcher:
    :params address:
    :params port:
    :params kwargs:
    """
    s = server.StreamServer((address, int(port)), dispatcher, **kwargs)
    return s


if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    [parser.add_argument(i[0], default=i[1], help=i[2])
            for i in [('-b', '127.0.0.1:8080', 'endpoint that server bindto'),
                     ('-m', 'time', 'register module'),
                     ('-c', '', 'connect endpoint'),
                     ('-i', '', 'invoke method name'),
                     ('-a', '', 'args')]]
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    if not args.c:
        register_module(args.m)
        rpc = new_server(default_dispatcher, *args.b.split(":"))
        rpc.serve_forever()
    
    client = Client(tuple(args.c.split(":")))
    print client(args.i, *args.a.split(','))
