#!/usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='justrpc',
      version='0.2.1',
      description="Fast and simple JSON RPC v1.0 for TCP connection",
      install_requires=['gevent', 'python-cjson'],
      long_description="",
      author="Meng Zhuo",
      author_email="mengzhuo1203+justrpc@gmail.com",
      url="http://github.com/mengzhuo/justrpc",
      py_modules=['justrpc'],
      license='GPL2',
      platforms='any',
      classifiers=['Development Status :: 3 - Alpha',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: MIT License',
                    'Programming Language :: Python :: 2.6',
                    'Programming Language :: Python :: 2.7',
          ],

        entry_points={
              'console_scripts': [
                  'jrpc = justrpc:_main'
              ]
        }

      )
