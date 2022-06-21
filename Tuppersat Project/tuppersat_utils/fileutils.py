"""
tuppersat.utils.fileutils

"""

# standard library imports
import time
from queue import Queue

# UCD TupperSat related imports
from tuppersat.utils.threadutils import ConsumerThread


# ****************************************************************************

def timestamped(msg, time_fmt='unix', sep='\t'):
    """Add a timestamp to a message.

    For the time format, this accepts either the string 'unix', which gives
    the system clock UNIX timestamp formatted as a float to 6 decimal
    places. This is the default behaviour.

    See docs.python.org/3/library/time.html#time.strftime for more information
    about allowed format specifiers for time.strftime.

    """

    if time_fmt == 'unix':
        _timestamp = f'{time.time():.6f}'
    else:
        _timestamp = time.strftime(time_fmt, time.localtime())

    return f'{_timestamp}{sep}{msg}'



# ****************************************************************************

class OutputFile:
    """A thread-safe file output."""
    def __init__(self, filename, mode='w', buffering=1, encoding=None,
                 timeout=1):
        """Initialiser.

        ==========
        Parameters
        ==========

        filename, mode, buffering, encoding are passed to the built-in open.

        timeout is passed to ConsumerThread

        """
        # file arguments
        self._filename  = filename
        self._mode      = mode
        self._buffering = buffering
        self._encoding  = encoding
        
        # consumer thread arguments
        self._timeout  = timeout
        
        self._queue = Queue()

    def __repr__(self):
        return f'OutputFile({self._filename}, mode={self._mode})'        

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
        
    def open(self):
        self._file = open(
            self._filename             ,
            mode      = self._mode     ,
            buffering = self._buffering,
            encoding  = self._encoding ,
        )

        self._thread = ConsumerThread(
            queue   = self._queue        ,
            func    = self._write_to_file,
            timeout = self._timeout      ,
        )
        self._thread.start()

    def close(self):
        self._thread.stop()
        self._file.close()


    def _write_to_file(self, msg):
        """Internal method to write to file."""
        self._file.write(msg)

    def write(self, msg):
        """Write string to file.

        Internally, this uses a Queue to ensure thread-safety.
        """
        self._queue.put(msg)

    def writeline(self, msg, newline='\n'):
        """Write string to file with newline termination.

        Internally, this uses a Queue to ensure thread-safety.
        """
        self.write(msg+newline)
