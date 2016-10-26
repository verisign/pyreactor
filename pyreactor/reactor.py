# -*- coding: utf-8 -*-
"""
a multiprocessing reactor
"""

import Queue
import logging
import multiprocessing
import pprint
import os
import sys
import time
import traceback

from pyreactor import Error

__all__ = ['Reactor']

# Initialize logging.
logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())


class Reactor(object):
    """
    Leverages multiprocessing to carry out concurrent tasks.

    :var.parallelism: nb of workers by default.
    :var.result_timeout: time to wait for result of a task (secs)

                            - recommended to be the max time it might take for a
                              task to complete
    :var.correlate_tasks_to_results: whether we correlate tasks to results

                                        - If True, provide list of tuple::

                                                [(<task>, <result>),
                                                (<task>, <result>)]

                                        - Else provide list of result's::

                                                [<result>, <result>]

    """
    # nb of workers by default
    parallelism = 5

    # time to wait for result of a task (secs)
    result_timeout = 300

    # whether we correlate tasks to results
    correlate_tasks_to_results = False

    def __init__(self, stop_on_error, parallelism=parallelism,
                 result_timeout=result_timeout):
        """
        Initializer.

        :param stop_on_error: stop all workers if there is an exception in any
                             one of them.
        :type stop_on_error: bool
        :param parallelism: degree of parallelism.
        :type parallelism: int
        :param result_timeout: time to wait (secs) for result of a task.

                                 - Recommended to set it to the max time it may
                                   take for a worker to process a result.
        :type result_timeout: int
        :return: None
        :rtype: None
        """
        self.stop_on_error = stop_on_error
        self.parallelism = parallelism
        self.result_timeout = result_timeout

        # if true; run enslaved task
        self.__fire = False

        # a pool of workers
        self.__workers = []

        # a bunch of tasks
        self.__tasks = multiprocessing.Queue()

        # results of tasks
        self.__results = multiprocessing.Queue()

        # results to be returned to the caller
        self.final_results = []

        # any errors
        self.__errors = multiprocessing.Queue()

        # signalling channel to workers to stop if something goes wrong
        self.__stop_channel = multiprocessing.Queue()

        # enslaved action
        self.__action = None

        # the tasks that the user has entrusted us with
        self.tasks = None

        # error by any of the workers
        self.error = None

        # set to indicate that the reactor is unusable
        self.spent = False

    def run(self, tasks, action,
            correlate_tasks_to_results=correlate_tasks_to_results):
        """
        Distribute tasks amongst n workers.

        :param action: the action to be done using task data points. Must be
                       __callable__
        :type action: callable
        :param tasks: data points
        :type tasks: list of objects
        :param correlate_tasks_to_results: If True, then return a list of tuples
                                           of (<task>, <results>).
                                           Else, return a list of <results>.
        :type correlate_tasks_to_results: bool
        :return: list of results
        :rtype: list
        """
        self.correlate_tasks_to_results = correlate_tasks_to_results

        _time_format = '%d-%b-%Y %H:%M:%S %Z'  # 4-Feb-2016 09:14:52 EST

        self.__load_tasks(tasks)

        # enslave the action.
        self.__action = action

        if len(self.tasks) < self.parallelism:
            log_msg = "{} worker(s) work on {} tasks.".format(len(self.tasks),
                                                              len(tasks))
        else:
            log_msg = "{} worker(s) work on {} tasks.".format(self.parallelism,
                                                              len(tasks))
        logger.info(log_msg)
        log_msg = "Start time: {}".format(time.strftime(_time_format))
        logger.info(log_msg)
        _start_time = time.time()
        self.__run_workers()

        log_msg = 'Processing results.'
        logger.info(log_msg)
        self.__fetch_results()

        _end_time = time.time()
        log_msg = 'Finished processing.'
        log_msg += 'End time: {}'.format(time.strftime(_time_format))
        logger.info(log_msg)

        _duration = _end_time - _start_time
        log_msg = "---- {} secs ---- ".format(
            float("{0:.2f}".format(_duration)))
        logger.info(log_msg)

        # special stuff for errors in workers
        if self.error and self.stop_on_error:
            # let's wait for stop tokens to be acknowledged
            log_msg = 'master - waiting for stop tokens to be acknowledged.'
            logger.info(log_msg)

            # wait for workers to exit cleanly
            for _worker in self.__workers:
                _worker.join()

            # close out resources
            self.__tasks.close()
            self.__tasks.join_thread()
            self.__errors.close()
            self.__errors.join_thread()
            self.__results.close()
            self.__results.join_thread()

            self.spent = True

            raise Error(self.error)

        # business as usual; wait for workers to finish their job.
        for _worker in self.__workers:
            _worker.join()

        self.spent = True

        return self.final_results

    def __load_tasks(self, tasks):
        """
        Initialize task queue with task data-points and poison pills.

        :param tasks: list of job descriptions
        :type tasks: list of objects
        :return: None
        :rtype: None
        """
        self.tasks = tasks
        _poison_pill_ct = 0

        log_msg = 'Loading up task queue.'
        logger.debug(log_msg)

        for _task in tasks:
            self.__tasks.put(_task)

        # line up poison pills.
        if len(self.tasks) < self.parallelism:
            for i in xrange(len(self.tasks)):
                self.__tasks.put(None)
                _poison_pill_ct += 1
        else:
            for i in xrange(self.parallelism):
                self.__tasks.put(None)
                _poison_pill_ct += 1

        log_msg = 'Loaded task queue with {} tasks '.format(len(tasks))
        log_msg += 'and {} poison pills.'.format(_poison_pill_ct)
        logger.debug(log_msg)

    def __run_workers(self):
        """
        Fire off workers to work on tasks.

        :return: None
        :rtype: None
        """
        # light the fuse.
        self.__fire = True

        if len(self.tasks) < self.parallelism:
            log_msg = 'Fewer tasks than parallelism; spawning fewer workers.'
            logger.info(log_msg)

            for i in xrange(len(self.tasks)):
                self.__workers.append(
                    # multiprocessing.Process(target=self.__action,
                    #                         name='worker_%s' % i))
                    multiprocessing.Process(target=self.__enslave,
                                            name='worker_%s' % i))

        else:
            for i in xrange(self.parallelism):
                self.__workers.append(
                    # multiprocessing.Process(target=self.__action,
                    #                         name='worker_%s' % i))
                    multiprocessing.Process(target=self.__enslave,
                                            name='worker_%s' % i))

        log_msg = 'Initialized {} workers.'.format(len(self.__workers))
        logger.info(log_msg)

        # start workers
        for (_worker_nb, _worker) in enumerate(self.__workers):
            log_msg = 'Starting worker {}'.format(_worker_nb)
            logger.debug(log_msg)
            _worker.start()

    # noinspection PyBroadException,PyUnusedLocal
    def __enslave(self):
        """
        A closure to condemn the action to the mundane world of multiprocessing.

        :return: None
        :rtype: None
        """
        _worker_name = multiprocessing.current_process().name

        log_msg = 'Started {}, pid: {}, ppid: {}'.format(_worker_name,
                                                         os.getpid(),
                                                         os.getppid())
        logger.info(log_msg)

        while True:
            # no errors to begin with!!
            _stop = None

            # check if we need to worry about stop tokens.
            try:
                if self.stop_on_error:

                    log_msg = '{} '.format(_worker_name)
                    log_msg += 'checking for stop tokens.'
                    logger.debug(log_msg)

                    _stop = self.__stop_channel.get(block=True, timeout=1)

                    if _stop is not None:
                        log_msg = '{} '.format(_worker_name)
                        log_msg += 'got a stop token. '
                        logger.warn(log_msg)

                    if _stop == 'stop':
                        log_msg = '{} '.format(_worker_name)
                        log_msg += 'got a valid stop token; stopping actions.'
                        logger.warn(log_msg)

                        # prevent deadlocks
                        log_msg = '{} '.format(_worker_name)
                        log_msg += 'flushing tasks.'
                        logger.debug(log_msg)
                        while True:
                            _task = self.__tasks.get()
                            if _task is None:
                                # the poison pill
                                return

            except Queue.Empty:

                log_msg = '{} '.format(_worker_name)
                log_msg += 'got no stop tokens; keep working.'
                logger.debug(log_msg)

            # actions on tasks
            log_msg = '{} '.format(_worker_name)
            log_msg += 'fetching tasks.'
            logger.debug(log_msg)

            _task = self.__tasks.get()

            if _task is None:
                # the poison pill
                log_msg = '{} '.format(_worker_name)
                log_msg += 'finished all tasks.'
                logger.info(log_msg)
                return

            try:
                _result = self.__action(_task)

                if self.correlate_tasks_to_results:
                    _result = (_task, _result)

                self.__results.put(_result)
            except Exception as e:
                log_msg = '{} '.format(_worker_name)
                log_msg += 'has had an exception. Adding to error queue. '
                log_msg += 'Exception details: {}'.format(e.args[0])
                logger.error(log_msg)
                if self.correlate_tasks_to_results:
                    _result = (_task, None)
                else:
                    _result = None

                self.__results.put(_result)
                self.__errors.put(
                    "".join(traceback.format_exception(*sys.exc_info())))

    def __fetch_results(self):
        """
        Process results from the slave worker.
          - Populate the final list of results to be returned to the user.
          - Will take care of stopping other workers if one of them had signaled
            an error.
          - Max number of results must equal the number of tasks.
             - If not, then will wait for result_timeout secs before assuming
               that all processing is completed.

        :return: None
        :rtype: None
        """

        # max number of results equal number of tasks
        for i in xrange(len(self.tasks)):

            if self.stop_on_error:
                log_msg = 'master - checking for errors in workers.'
                logger.debug(log_msg)
                try:
                    # wait for the worker to act; and block for some time.
                    if i == 0:
                        _error = self.__errors.get(block=True, timeout=1)
                    else:
                        _error = self.__errors.get(block=False)

                    if _error:
                        # some worker has had an error; signal on stop channel
                        log_msg = 'master - worker signaled an exception'
                        log_msg += 'error info: {}'.format(_error)
                        logger.error(log_msg)

                        log_msg = 'signaling error to other workers.'
                        logger.warn(log_msg)

                        # noinspection PyUnusedLocal
                        for _worker in self.__workers:
                            self.__stop_channel.put('stop')

                        self.error = _error
                        return
                except Queue.Empty:
                    log_msg = 'master - no exception in any of the workers.'
                    logger.debug(log_msg)

            # process results
            try:
                log_msg = 'master - fetching result '
                log_msg += '(will block for {} secs)'.format(
                    self.result_timeout)
                logger.debug(log_msg)
                _result = self.__results.get(block=True,
                                             timeout=self.result_timeout)
                log_msg = 'master - got result {}'.format(
                    pprint.pformat(_result))
                logger.debug(log_msg)
                self.final_results.append(_result)

            except Queue.Empty:
                # done with all tasks
                log_msg = 'master - finished fetching all results.'
                logger.info(log_msg)

                break
