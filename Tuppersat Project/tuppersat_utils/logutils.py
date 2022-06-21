"""
tuppersat.utils.logutils


"""
# standard library imports
import logging
from contextlib import contextmanager

# local imports
from .scriptutils import timestamped_filename 


# TODO: add function to add standard logging options to command line argument
# parser?

# ****************************************************************************
# logging configuration toolkit
# ****************************************************************************

LOG_FORMAT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'

def configure_logging(logger=None, verbose=False, filename=None,
                      fmt=LOG_FORMAT):
    """Simple setup of the root logger.

    Unlike logging.basicConfig, this always writes to a StreamHandler, and
    optionally writes to a FileHandler

    ==========
    Parameters
    ==========
    logger : [optional] 
        Logger to be configured (defaults to root)

    verbose : bool [optional]
        True sets logging level to  DEBUG

    filename : [optional]
        if None output only to stderr; if True or string, write to a log file
   
    fmt : [optional]
        the logging format to be used

    """
    import logging

    if logger is None:
        logger = logging.getLogger()

    # select the logging detail
    _level = (logging.DEBUG if verbose else logging.INFO)

    # create a Formatter object
    _fmtr = logging.Formatter(fmt)
    
    # create stream handler
    _handlers = [logging.StreamHandler(),]

    # optionally create a file handler
    if filename is not None:
        if filename == True:
            # use default
            _filename = timestamped_filename(ext='.log')
        else:
            _filename = filename

        _handlers.append(logging.FileHandler(_filename))

    # configure the logger and attach the individual handlers
    logger.setLevel(_level)
    for _handler in _handlers:
        _handler.setLevel(_level)
        _handler.setFormatter(_fmtr)
        logger.addHandler(_handler)
        
    return logger



# ****************************************************************************
# log the successful completion of an action
# ****************************************************************************

@contextmanager
def log_action(log, msg, level=logging.DEBUG):
    """Context manager to log the start and end of a code block."""
    # initial log statement
    log.log(level, msg)

    # perform action
    yield
    
    # completion log statement -- only runs if no error raised
    log.log(level, f'{msg} -- DONE')

# ****************************************************************************
