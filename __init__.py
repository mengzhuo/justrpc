#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

from handler import dispatcher, new_server

if __name__ == '__main__':

    def add(x, y):
        return x+y

    dispatcher.register(add)
    server = new_server('127.0.0.1', 8080)
    server.serve_forever()
