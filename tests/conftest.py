# -*- coding: utf-8 -*-

import sys

import os.path
# noinspection PyPackageRequirements
import pytest
from pyreactor.reactor import Reactor

sys.path.append(os.path.join(os.getcwd(), '.'))
sys.path.append(os.path.join(os.getcwd(), '..'))


@pytest.fixture(scope='function')
def get_no_stop_on_error_reactor():
    """
    Provide a standard no-stop-on-error reactor object.

    :return: reactor fixture
    :rtype: pyreactor.reactor.Reactor
    """
    _reactor = Reactor(stop_on_error=False, parallelism=5,
                       result_timeout=300)
    return _reactor


@pytest.fixture(scope='function')
def get_stop_on_error_reactor():
    """
    Provide a standard stop-on-error reactor object.

    :return: reactor fixture
    :rtype: pyreactor.reactor.Reactor
    """
    _reactor = Reactor(stop_on_error=True, parallelism=5,
                       result_timeout=300)
    return _reactor
