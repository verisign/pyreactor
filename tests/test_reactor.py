# -*- coding: utf-8 -*-
"""
test_reactor.py

Unit tests for reactor.py
"""
import logging
from time import sleep

# noinspection PyPackageRequirements
import pytest

import pyreactor
from pyreactor.reactor import Reactor

# Initialize logging.
logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())


# logger = logging.getLogger()
# handler = logging.StreamHandler()

# format_str = 'pid-%(process)d %(asctime)s %(filename)s: Line # %(lineno)s'
# format_str += ', %(name)s:%(funcName)s - %(levelname)s - %(message)s'
# formatter = logging.Formatter(format_str)

# handler.setFormatter(formatter)

# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)


def add_5(x):
    """
    Sample action. Add 5 to a number.

    :param x: the task
    :type x: int or float
    :return: 5 more than number
    :rtype: int or float
    """
    log_msg = 'Adding 5 to {}'.format(x)
    logger.info(log_msg)
    return x + 5


def sleeping_add_5(x):
    """
    Sample action. Add 5 to a number; with some sleep

    :param x: the task
    :type x: int or float
    :return: 5 more than number
    :rtype: int or float
    """
    sleep(1)
    return x + 5


class TestReactor(object):
    """
    Unit tests for Reactor.
    """

    def test_init(self):
        _reactor = Reactor(stop_on_error=False, parallelism=5,
                           result_timeout=300)

        assert isinstance(_reactor, Reactor)
        assert _reactor.stop_on_error is False
        assert _reactor.parallelism == 5
        assert _reactor.result_timeout == 300

        _reactor = Reactor(stop_on_error=True, parallelism=5,
                           result_timeout=300)

        assert isinstance(_reactor, Reactor)
        assert _reactor.stop_on_error is True
        assert _reactor.parallelism == 5
        assert _reactor.result_timeout == 300

    def test_no_stop_on_error_reactor(self, get_no_stop_on_error_reactor):
        """
        test a no-stop-on-error reactor

        :param get_no_stop_on_error_reactor: fixture; a no stop on error reactor
        :type get_no_stop_on_error_reactor: reactor.Reactor
        :return:
        """
        _reactor = get_no_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=add_5, tasks=_tasks)

        assert isinstance(_results, list)
        assert set(_results) == {6, 7, 8, 9, 10}

    def test_no_stop_on_error_reactor_long_tasks(self,
                                                 get_no_stop_on_error_reactor):
        _reactor = get_no_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=sleeping_add_5, tasks=_tasks)

        assert isinstance(_results, list)
        assert set(_results) == {6, 7, 8, 9, 10}

    def test_no_stop_on_error_reactor_with_exceptions(
            self, get_no_stop_on_error_reactor):
        _reactor = get_no_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5, 'a', 'b', 6]

        _results = _reactor.run(action=add_5, tasks=_tasks)

        assert isinstance(_results, list)
        assert set(_results) == {6, 7, 8, 9, 10, None, None, 11}

    def test_stop_on_error_reactor(self, get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=add_5, tasks=_tasks)

        assert isinstance(_results, list)
        assert set(_results) == {6, 7, 8, 9, 10}

    def test_stop_on_error_reactor_long_tasks(self, get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=sleeping_add_5, tasks=_tasks)

        assert isinstance(_results, list)
        assert set(_results) == {6, 7, 8, 9, 10}

    def test_stop_on_error_reactor_with_exceptions(self,
                                                   get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        # will fail if the action is quick on the tasks and you are towards
        # the end of the list of tasks!!
        _tasks = ['q', 1, 2, 3, 4, 5, 'a', 'b', 6]

        with pytest.raises(pyreactor.Error) as exc_info:
            _results = _reactor.run(action=add_5, tasks=_tasks)

        _exception_str = "TypeError: cannot concatenate 'str' and 'int' objects"
        assert _exception_str in str(exc_info.value)

    def test_stop_on_error_reactor_with_exceptions_in_end(
            self, get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5, 'a', 'b']

        try:
            _results = _reactor.run(action=add_5, tasks=_tasks)
            assert isinstance(_results, list)
            assert set(_results) == {6, 7, 8, 9, 10, None, None}
        except pyreactor.Error as e:
            # log_msg = 'Had an exception in the end!!'
            # logger.info(log_msg)
            pass

    def test_no_stop_on_error_reactor_with_correlation(
            self, get_no_stop_on_error_reactor):
        _reactor = get_no_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=add_5, tasks=_tasks,
                                correlate_tasks_to_results=True)

        assert isinstance(_results, list)
        assert set(_results) == {(1, 6), (2, 7), (3, 8), (4, 9), (5, 10)}

    def test_no_stop_on_error_reactor_long_tasks_with_correlation(
            self, get_no_stop_on_error_reactor):
        _reactor = get_no_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=sleeping_add_5, tasks=_tasks,
                                correlate_tasks_to_results=True)

        assert isinstance(_results, list)
        assert set(_results) == {(1, 6), (2, 7), (3, 8), (4, 9), (5, 10)}

    def test_no_stop_on_error_reactor_with_exceptions_with_correlation(
            self, get_no_stop_on_error_reactor):
        _reactor = get_no_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5, 'a', 'b', 6]

        _results = _reactor.run(action=add_5, tasks=_tasks,
                                correlate_tasks_to_results=True)

        assert isinstance(_results, list)
        assert set(_results) == {(1, 6), (2, 7), (3, 8), (4, 9), (5, 10),
                                 ('a', None), ('b', None), (6, 11)}

    def test_stop_on_error_reactor_with_correlation(self,
                                                    get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=add_5, tasks=_tasks,
                                correlate_tasks_to_results=True)

        assert isinstance(_results, list)
        assert set(_results) == {(1, 6), (2, 7), (3, 8), (4, 9), (5, 10)}

    def test_stop_on_error_reactor_long_tasks_with_correlation(
            self, get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5]

        _results = _reactor.run(action=sleeping_add_5, tasks=_tasks,
                                correlate_tasks_to_results=True)

        assert isinstance(_results, list)
        assert set(_results) == {(1, 6), (2, 7), (3, 8), (4, 9), (5, 10)}

    def test_stop_on_error_reactor_with_exceptions_with_correlation(
            self, get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        _tasks = ['q', 1, 2, 3, 4, 5, 'a', 'b', 6]

        with pytest.raises(pyreactor.Error) as exc_info:
            _results = _reactor.run(action=add_5, tasks=_tasks,
                                    correlate_tasks_to_results=True)

        _exception_str = "TypeError: cannot concatenate 'str' and 'int' objects"
        assert _exception_str in str(exc_info.value)

    def test_stop_on_error_reactor_with_exceptions_with_correlation_2(
            self, get_stop_on_error_reactor):
        _reactor = get_stop_on_error_reactor

        _tasks = [1, 2, 3, 4, 5, 'a', 'b', 6]

        try:
            _results = _reactor.run(action=add_5, tasks=_tasks)
            assert isinstance(_results, list)
            assert set(_results) == {6, 7, 8, 9, 10, None, None, 11}
        except pyreactor.Error as e:
            # log_msg = 'Had an exception in the end!!'
            # logger.info(log_msg)
            pass

    def test_no_stop_on_error_reactor_fewer_tasks_than_workers(
            self, get_no_stop_on_error_reactor):
        """
        test a no-stop-on-error reactor

        :param get_no_stop_on_error_reactor: fixture; a no stop on error reactor
        :type get_no_stop_on_error_reactor: reactor.Reactor
        :return:
        """
        _reactor = get_no_stop_on_error_reactor

        _tasks = [1, 2, 3]

        _results = _reactor.run(action=add_5, tasks=_tasks)

        assert isinstance(_results, list)
        assert set(_results) == {6, 7, 8}
