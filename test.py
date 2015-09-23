#!/usr/bin/env python
# encoding: utf-8

import unittest

class TestDispatcher(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        from justrpc import Dispatcher
        self.dis = Dispatcher()

    def tearDown(self):
        pass

    def test_add(self):
        from justrpc import MethodAlreadyRegisted
        def Add(x, y):
            pass
        self.dis.register(Add)
        self.assertIn('Add', self.dis.funcs)
        self.assertRaises(MethodAlreadyRegisted, self.dis.register, Add)
