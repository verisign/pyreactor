#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import time

import os


def add(a, b):
    """
    Adds two numbers.

    :param a: number
    :type a: int
    :param b: number
    :type b: int
    :return: result of adding the two numbers
    :rtype: int
    """
    time.sleep(2)
    return a + b


def consumer(input_queue, result_queue, action):
    """
    the basic poison pill reactor

    :param input_queue: input queue
    :type input_queue: multiprocessing.Queue
    :param result_queue: result queue
    :type result_queue: multiprocessing.Queue
    :param action: action to perform on data points
    :type action: callable
    :return:
    """
    _iteration = 0
    _blow_up_iteration = 1

    print 'consumer pid: {} initialized!!'.format(os.getpid())

    while True:
        _iteration += 1
        print 'consumer pid: {}; iteration # {}'.format(os.getpid(), _iteration)
        if _iteration == _blow_up_iteration:
            log_msg = '------- '
            log_msg += 'exception in consumer; pid: {} iteration # {}'.format(
                os.getpid(), _iteration)
            log_msg += ' -------'
            raise Exception(log_msg)

        _data_point = input_queue.get()
        # poison pill
        if _data_point is None:
            print 'consumer pid: {} iteration {}, got poison-pill'.format(
                os.getpid(), _iteration)
            break

        print 'consumer pid: {} iteration {}, got data-point {}'.format(
            os.getpid(), _iteration, _data_point)

        result = action(*_data_point)
        result_queue.put(result)

    return


def producer():
    input_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    parallelism = 2

    # stuff to work on
    data_points = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
    for _d in data_points:
        input_queue.put(_d)

    # poison pills
    for i in xrange(parallelism):
        input_queue.put(None)

    # parallelized action
    consumers = []
    for i in xrange(2):
        _c = multiprocessing.Process(target=consumer,
                                     args=(input_queue, result_queue, add))
        consumers.append(_c)

    print 'producer pid: {}'.format(os.getpid())
    # start consumers
    for _index, _c in enumerate(consumers):
        _c.start()
        print 'producer: started worker # {}: pid: {}'.format(_index + 1,
                                                              _c.pid)

    # close off input queues
    input_queue.close()  # no more data points
    input_queue.join_thread()  # wait for feeder thread to flush the buffer

    # let's wait for consumers to complete their tasks
    for _index, _c in enumerate(consumers):
        print 'producer: joined worker # {}'.format(_index + 1)
        _c.join()
        print 'producer: exit code of worker # {}: {}'.format(_index + 1,
                                                              _c.exitcode)

    print 'all consumers finished working'

    # print results out
    print 'producer: fetching results'
    for _i in xrange(len(data_points)):
        _result = result_queue.get()
        print 'Result: {}'.format(_result)


def main():
    producer()


if __name__ == '__main__':
    main()
