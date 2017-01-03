# pyreactor
Reactor design pattern with [add-ons](#about)

![Pyreactor Architecture](./docs/pyreactor_architecture.png?raw=true "pyreactor architecture")

## Table of Contents
* [About](#about)
* [Use Cases](#use-cases)
* [System Requirements](#system-requirements)
* [Dependencies](#dependencies)
* [Installation](#installation)
* [Usage](#usage)
* [Cookbook](#cookbook)
* [Unit Tests](#unit-tests)
* [License](#license)
* [Aside](#aside)

## About
Implements the [reactor pattern](./docs/main.md#reactor-design-pattern) with the following add-on's:
 - `stop-on-error mode`: Stop overall processing if one consumer (worker) fails.
    - The first encountered exception with full traceback is provided to the caller.
        - User can use normal exception handling mechanisms to process exception.
    - Gracefully shut down remaining workers.
    - Drain task queues to prevent deadlocks.
 - `no-stop-on-error mode`: Continue processing despite an exception in one (or more) consumer(s)/worker(s).
    - Skip erroneous task and continue processing remaining tasks.
    - Consumer (worker) with the exception is kept alive and keeps consuming tasks.
 - Provides optional task to result correlation in either mode. See [cookbook](#cookbook) for more usage examples. 
 - Tested to prevent deadlocks.
 - Abstracts away the pattern from user; easy to [use](#usage).

## Use Cases

See [here](./docs/main.md#use-case-for-reactor-pattern)

## System requirements
- Currently tested on `Python 2.7.5`.

## Dependencies
No external dependencies.

## Installation

- Download source code.
```bash
git clone git@github.vrsn.com:EdgeopsChecks/pyreactor.git
```

- Install codebase.
```bash
cd pyreactor
sudo python setup.py install
```

## Usage
- An example of a no-stop-on-error reactor is below [(file)](./docs/cookbook/no_stop_on_error_pyreactor.py):
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from pyreactor.reactor import Reactor

def add_5(x):
    sleep_secs = 5
    log_msg = 'consumer pid {} - '.format(os.getpid())
    log_msg += 'Adding 5 to {}; after sleeping for {} secs'.format(x,
                                                                   sleep_secs)
    print log_msg
    time.sleep(sleep_secs)
    return x + 5

def main():
    # no-stop-on-error reactor; continue processing even if one consumer fails
    # result_timeout = max time taken to complete 1 task.
    reactor = Reactor(stop_on_error=False, parallelism=2,
                      result_timeout=10)

    # five tasks; will error on first one
    tasks = ['1', 2, 3, 4, 5]

    results = reactor.run(action=add_5, tasks=    tasks)

    print results
    
if __name__ == '__main__':
    main()
```

Output:
```bash
[None, 7, 9, 8, 10]
```

- An example of a stop-on-error reactor is below [(file)](./docs/cookbook/stop_on_error_pyreactor.py):
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from pyreactor.reactor import Reactor

def add_5(x):
    sleep_secs = 5
    log_msg = 'consumer pid {} - '.format(os.getpid())
    log_msg += 'Adding 5 to {}; after sleeping for {} secs'.format(x,
                                                                   sleep_secs)
    print log_msg
    time.sleep(sleep_secs)
    return x + 5

def main():
    # five tasks; will error on first one
    tasks = ['1', 2, 3, 4, 5]

    # stop-on-error reactor; stop processing even if one consumer fails
    reactor = Reactor(stop_on_error=True, parallelism=2,
                      result_timeout=10)

    results = reactor.run(action=add_5, tasks=tasks)

    print results
    
if __name__ == '__main__':
    main()
```

Output:
```bash
Traceback (most recent call last):
  File "stop_on_error_pyreactor.py", line 60, in <module>
    main()
  File "stop_on_error_pyreactor.py", line 54, in main
    results = _reactor.run(action=add_5, tasks=tasks)
  File "../pyreactor/reactor.py", line 178, in run
    raise Error(self.error)
pyreactor.Error: Traceback (most recent call last):
  File "../pyreactor/reactor.py", line 309, in __enslave
    _result = self.__action(_task)
  File "stop_on_error_pyreactor.py", line 42, in add_5
    return x + 5
TypeError: cannot concatenate 'str' and 'int' objects
```

- See [docs](./docs/main.md) for further details.

## Cookbook

See [here](./docs/cookbook)

Cookbook examples may be run as follows:
```bash
cd pyreactor

# running no_stop_on_error_pyreactor.py for example
python cookbook/no_stop_on_error_pyreactor.py
```

## Unit Tests.
- py.test is used as a unit testing framework.
- Tests can be executed as follows:
```bash
py.test tests --color=yes -s --verbose -r X
```

##  License

The project is licensed under the BSD-3 license.

## Aside
- The code hasn't been tested to be thread safe.
- No tasks can be 'None'; it's a token to signal end of tasks.
