# -*- coding: utf-8 -*-
"""
__init__.py

High level stuff.
"""

import logging
import sys

import os

__version__ = (1, 0, 0)

# Update syspath.
file_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.abspath(os.path.join(file_dir, ".")))

# Initialize logging.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Error(Exception):
    """
    A generic Exception class.
    """

    def __init__(self, message=''):
        super(Error, self).__init__(message)
        if not message:
            log_msg = 'Generic exception message for pyreactor project.'
            self.message = log_msg
