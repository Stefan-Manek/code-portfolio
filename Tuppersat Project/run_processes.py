#Importing standard libraries
from threading import Event

#Importing custom libraries
import thread_utils as tu


############################################################

def process_thread(process, stop_event):
    """Function to loop process in a thread with stop event"""
    return tu.loop_thread(
        loop = process.update,
        setup = process.setup,
        teardown = process.teardown,
        stop_event = stop_event
        )

class RunProcesses:
    """Class to run all listed processes as separate threads"""
    def __init__(self, processes):
        """Initialisation"""
        
        # List of all processes to be executed
        self._processes = processes
        
        self._stop_event = Event()
        
        #List of threads for all processes:
        self._threads = [process_thread(process, self._stop_event)
                         for process in self._processes]
        
    
    def __enter__(self):
        self.setup()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()
        
    def setup(self):
        """Setup by starting all process threads"""
        tu.start_threads(self._threads)
    
    def teardown(self):
        """Teardown by stopping all threads"""
        tu.stop_threads(self._stop_event, self._threads)
        
    def loop(self):
        """No loop method required"""
        pass
    
    
