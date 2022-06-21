from threading import Thread
from class_utils import run

def loop_thread(loop, setup=None, teardown=None, stop_event=None):
    """Creates thread running sensor class until 
    stop_event is set to True"""
    
    def keep_running():
        """Returns opposite condition of stop event
        e.g. if stop_event == False, keep_running == True"""
        
        return not stop_event.is_set()
    
    return Thread(
        target = run,
        args=(loop, setup, teardown, keep_running)
        )

def sensor_thread(sensor, stop_event):
    """Creates thread running a specific sensor until 
    stop_event is True"""
    
    return loop_thread(
        loop = sensor.update,
        setup = sensor.setup,
        teardown = sensor.teardown,
        stop_event = stop_event
        )

def start_threads(threads):
    """Input: List of threads
    Starts all input threads"""
    for thread in threads :
        thread.start()
        
def stop_threads(event, threads):
    """Input: List of threads
    Stops all input threads"""
    # trigger stop_event
    event.set()
    # wait for the threads to finish
    for thread in threads:
        # end threads
        thread.join()
