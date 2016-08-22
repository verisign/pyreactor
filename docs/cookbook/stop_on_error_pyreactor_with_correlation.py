#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import time

import os.path

sys.path.append(os.path.join(os.getcwd(), '.'))
sys.path.append(os.path.join(os.getcwd(), '..'))

from pyreactor.reactor import Reactor

logger = logging.getLogger()
handler = logging.NullHandler()
logger.addHandler(handler)


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
    _tasks = ['1', 2, 3, 4, 5]

    # no-stop-on-error reactor; continue processing even if one consumer fails
    # result_timeout: max time taken to complete 1 task
    _reactor = Reactor(stop_on_error=True, parallelism=2,
                       result_timeout=10)

    _results = _reactor.run(action=add_5, tasks=_tasks)

    print _results


if __name__ == '__main__':
    main()
