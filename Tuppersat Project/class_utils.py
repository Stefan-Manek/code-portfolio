import time
import contextlib

@contextlib.contextmanager
def catch_and_suppress(*exc, callback=None):
    """ Context manager to suppress specified exception types."""
    try:
        yield
    except exc as e:
        if callback:
            callback(e)
    return


    
def repeat(target, condition=None):
    """ Repeat target indefinitely , or until optional condition is met .
    Inputs :
    target : callable
    the function to be run on repeat
    condition : callable [ optional ]
    a function whose result is used to determine with to continue with
    the next iteration of the loop . If condition is provided , the loop
    keeps running so long as condition returns True .
    """
    while (True if condition is None else condition()):
        target()



def run(loop, setup=None, teardown=None, keep_running=None):
    """Function to run all three processes"""
    if setup:
        setup()
    try :
        repeat(loop, keep_running)
    finally :
        if teardown:
            teardown()

        
        
def loop(sensor):
    """Looping read and update processes"""
    def _loop():
        sensor.update()
        # Printing each update
        print(f"{time.time():.6f} : {sensor._data}")
    return _loop



    
