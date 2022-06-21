"""
tuppersat.utils.threadutils


"""

# standard library imports
import queue
import threading
from time import time, sleep


class LoopThread(threading.Thread):
    """Execute function in infinite loop with optional setup & teardown."""
    def __init__(self, loop, setup=None, teardown=None):
        """Initialiser."""
        self._stop_event = threading.Event()

        self._loop     = loop
        self._setup    = setup
        self._teardown = teardown
        
        super().__init__()

    def run(self):
        self.setup()
        try:
            while self.is_running():
                self.loop()

        finally:
            self.teardown()

    def setup(self):
        if self._setup:
            self._setup()

    def teardown(self):
        if self._teardown:
            self._teardown()

    def loop(self):
        self._loop()
                
    def is_running(self):
        return not self._stop_event.is_set()
        
    def stop(self):
        """Terminate the looped thread's execution."""
        self._stop_event.set()
        self.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        return False



        
# ****************************************************************************

class ScheduleThread(LoopThread):
    """Schedule function to run in infinite loop at regular intervals."""
    def __init__(self, loop, interval, setup=None, teardown=None):
        self._interval = interval

        super().__init__(loop, setup, teardown)

    def setup(self):

        # perform any custom setup
        super().setup()
        
        # set the timer start time
        # TODO: allow this to be supplied by user? 
        self._next_time = time()


    def loop(self):
        if self._block_until_next_time():
            self._loop()

    def _block_until_next_time(self):
        """.

        Returns either True or False, depending on how it reaches its end: True
        indicates that it ran to timeout, and so it is time for the next
        iteration of the function. False indicates that the function was
        interrupted early by the user (ie, ScheduleThread.stop was called) and
        the next iteration of the function should not be run.

        """
        # TODO: what happens if _loop takes longer than interval to complete?
        # Current behaviour is that Event.wait returns immediately, but
        # self._next_time can get further and further behind the current
        # time. Should this  function skip missed appointments?
        
        # set the time for the next iteration
        self._next_time += self._interval

        # calculate the time remaining until the next iteration is due
        _timeout = self._next_time - time()

        # threading.Event.wait blocks until either:
        # -- time out completes (returns False); or
        # -- Event.set is called (returns True).

        return (not self._stop_event.wait(_timeout))

    
# ****************************************************************************

class ConsumerThread(LoopThread):
    """Waits for items in a Queue and consumes them."""
    def __init__(self, queue, func, timeout):
        """Initialisation."""
        self.queue = queue
        self._func = func

        self._timeout = timeout

        super().__init__(loop=None)
        
    def loop(self):
        consume(self.queue, self._func, self._timeout)

        
def consume(q, func, timeout=None):
    """
    Gets the next item from Queue q and performs func on it.

    If q is empty, waits for up to timeout seconds before timing out.
    """
    # TODO: should this return a value here? 
    try:
        item = q.get(timeout=timeout)
    except queue.Empty:
        pass
    else:
        func(item)


# ****************************************************************************

class ProducerThread(LoopThread):
    """Produces items and adds them to a Queue."""
    def __init__(self, queue, func):
        self.queue = queue
        self._func = func

        super().__init__(loop=None)

    def loop(self):
        produce(self.queue, self._func)



def produce(q, func):
    """Tries to create a new item and add it to a Queue for later use."""
    item = func()
    if item:
        q.put(item)


# ****************************************************************************

class ProducerConsumerThread(LoopThread):
    """Produces new items and immediately consumes them."""
    def __init__(self, producer, consumer):
        """Initialiser.

        The parameters producer and consumer must be callables that produce and
        consume items one at a time.

        """
        self._produce = producer
        self._consume = consumer

        super().__init__(loop=None)

    def loop(self):
        item = self._produce()
        if item:
            self._consume(item)
