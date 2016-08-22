#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import string
import sys
import time

import os.path

sys.path.append(os.path.join(os.getcwd(), '.'))
sys.path.append(os.path.join(os.getcwd(), '..'))

from pyreactor.reactor import Reactor

logger = logging.getLogger()
handler = logging.StreamHandler()
format_str = '%(levelname)s - %(message)s'
formatter = logging.Formatter(format_str)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def add_5(x):
    """
    Sample action. Add 5 to a number.

    :param x: the task
    :type x: int or float
    :return: 5 more than number
    :rtype: int or float
    """
    _sleep_secs = 5
    log_msg = 'consumer pid {} - '.format(os.getpid())
    log_msg += 'Adding 5 to {}; after sleeping for {} secs'.format(x,
                                                                   _sleep_secs)
    logger.warn(log_msg)
    time.sleep(_sleep_secs)
    return x + 5


def main():
    # five tasks
    _tasks = ['1', 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # no-stop-on-error reactor; continue processing even if one consumer fails
    # result_timeout: max time taken to complete 1 task
    _reactor = Reactor(stop_on_error=True, parallelism=3,
                       result_timeout=10)

    _results = _reactor.run(action=add_5, tasks=_tasks)

    print _results


if __name__ == '__main__':
    print '*' * 80
    log_msg = ' turning on logging; workers exit gracefully '
    log_msg += 'when one has an exception '
    log_msg = string.center(log_msg, 80, '*')
    print log_msg
    print '*' * 80
    main()
