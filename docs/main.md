## Reactor design pattern.
> The reactor design pattern is an event handling pattern for handling
> service requests delivered concurrently to a service handler by one or
> more inputs. The service handler then demultiplexes the incoming
> requests and dispatches them synchronously to the associated request
> handlers.
> 
> -- <cite>Wikipedia</cite>

## Use case for reactor pattern
Let's say we would like to execute an operation on a series of data
points (eg. servers / network gear). We also know the data points in
advance; i.e. we are not generating them on-the-fly.

We can leverage the python `multiprocessing` module coupled with the
[poison-pill method](#poison-pill-method).

## Poison Pill Method

See [here](https://pymotw.com/2/multiprocessing/communication.html) for an excellent example.

![Poison Pill](./poison_pill_basic.png?raw=true "basic poison pill algorithm")

The basic idea is as follows:
 - The producer instantiates a couple of `multiprocessing.Queue`: 
    - The first is an `input_queue` to which the list of data-points (`[d1, d2, d3, ..., dn]`) are fed.
    - The second is a `result_queue` that holds the result of processing by the consumer.
 - The producer instantiates a bunch of consumer processes; `multiprocessing.Process` in effect that exec's an action.
    - Number of consumers are defined by degree of parallelism.
 - Producer fires off the processes and wait on their completion.
 - The consumers: 
    - Dequeues data-points off the `input_queue` and process them.
    - Output is placed on the `result_queue`. (`[d1', d2', d3', ..., dn']`)
    - Each worker continues to dequeue until it hits a poison pill.
        - At this point the worker exits.
 - The caller then collects all the results and does the needful.

## Potential pitfalls of this approach.
- If there is an exception in a consumer (worker), the producer (caller) will have to block till the remaining workers finish their tasks.
    - See [demo](./poison_pill_basic_demo_exception_in_one_worker.py).

      ```bash
      python poison_pill_basic_demo_exception_in_one_worker.py
      ````
    - This can be annoying; especially if the number of sample size of the data-points is large.
    - The exception is hidden; it's not propagated back to caller.
    - The programmer is expected to know the subtleties of the `multiprocessing` module.
    - Anytime there is an exception, the worker dies; and instead of `n` workers doing the job, we have `n-1` workers doing the job. 
      If the number of data-points is large, and all the workers perish due to exceptions, we have a deadlock. See [here](./poison_pill_basic_demo_exception_in_all_workers.py)
       
       ```bash
      python poison_pill_basic_demo_exception_in_all_workers.py
      ````

## Pyreactor

![Pyreactor Architecture](./pyreactor_architecture.png?raw=true "pyreactor architecture")

The main problem in the poison pill approach above was the lack of inter-worker communication. Then there was the potential of deadlocks if all workers had exceptions.

`pyreactor` solves both these problems by introducing two more queues:
  - `error_queue`: keeps track of exceptions raised by the workers.
  - `stop_queue`: distributes stop tokens to children if there is an exception in any one of them (and the user has asked for a stop-on-error reactor)

`pyreactor` also presents a simple interface to the user:
 ```python
from pyreactor.reactor import Reactor

def add_5(x):
    return x + 5 

# no-stop-on-error rector
reactor = Reactor(stop_on_error=False, parallelism=2, result_timeout=2)
results = reactor.run(tasks=[1,2,3], action=add_5)
 ```

An exception in one worker is now tracked in the `error_queue` and if the user has invoked a no-stop-on-error reactor, then the worker is kept alive.

If the user invokes a stop-on-error reactor as below:
 ```python
from pyreactor.reactor import Reactor

def add_5(x):
    return x + 5 

# stop-on-error rector
reactor = Reactor(stop_on_error=True, parallelism=2, result_timeout=2)
results = reactor.run(tasks=[1,2,3], action=add_5)
 ```

The first exception registered in `error_queue` is detected and stop tokens are distributed via the `stop_queue` and the `input_queue` is drained off.
On the next iteration, `pyreactor` workers check the `stop_queue` and gracefully exit out. The exception with full traceback is propagated back to the caller.

## Caveats

Care should be taken to ensure that `result_timeout` should be set to be greater than the time taken to complete one task.
