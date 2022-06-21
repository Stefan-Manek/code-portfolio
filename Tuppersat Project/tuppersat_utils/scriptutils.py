"""
tuppersat.utils.scriptutils

"""
# standard library imports
import contextlib
import datetime as dt
import functools
import time

# ****************************************************************************
# argument decorator
# ****************************************************************************

# this basically reproduces functools.partial in a not necessarily clearer
# format. This is used as:
# 
# @fixed_arguments 
# def func(*args, **kwargs):
#     # do something
#
# callable = func(*args, **kwargs)
# 
# which is equivalent to
# 
# def func(*args, **kwargs)
#     # do something
# 
# callable = functools.partial(func, *args, **kwargs)
#
# So, I'm not convinced it adds anything other than reinventing the wheel. I
# should phase it out again!


def fixed_arguments(func):
    """Return a new callable with arguments fixed."""
    @functools.wraps(func)
    def _func_initialiser(*args, **kwargs):

        # TODO: should this be decorated with @functools.wraps(func)? 
        def _func_caller():
            return func(*args, **kwargs)

        return _func_caller
    return _func_initialiser


# ****************************************************************************
# task scheduling tools
# ****************************************************************************

#def delay(interval):
#    """Sleep until interval has passed since delay last completed."""
#    _next_time = None
#
#    def _func(*args, **kwargs):
#        nonlocal _next_time
#        # initialise the scheduler
#        if _next_time is None:
#            _next_time = time.time()
#
#        # increment the scheduler
#        _next_time += interval
#
#        # compute the remaining sleep time
#        _timeout = max([_next_time - time.time(), 0])
#
#        # pause
#        time.sleep(_timeout)
#
#        return True
#    return _func

def repeat(func, *args, **kwargs):
    """Repeat func indefinitely."""
    while True:
        func(*args, **kwargs)


def repeat_on_schedule(func, interval=0, *args, **kwargs):
    """Repeat func at intervals not less than interval."""
    _next_time = None
    while True:
        if _next_time is None:
            _next_time = time.time()

        # increment the scheduler
        _next_time += interval

        # compute the remaining sleep time
        _timeout = max([_next_time - time.time(), 0])

        # pause
        time.sleep(_timeout)

        # run function
        func(*args, **kwargs)


# ****************************************************************************
# 
# ****************************************************************************

@contextlib.contextmanager
def context(setup=None, teardown=None):
    """Handle setup and teardown."""
    if setup:
        setup()

    try:
        yield
    finally:
        if teardown:
            teardown()


@contextlib.contextmanager
def listen_for_interrupt(callback=None):
    """Contextmanager to handle KeyboardInterrupt."""
    try:
        yield
    except KeyboardInterrupt:
        if callback:
            callback()
    return

def run(loop, setup=None, teardown=None, interval=0):
    """Run loop on repeat, with optional setup and teardown.

    Note that the callables loop, setup, and teardown must take no additional
    arguments.

    """
    with context(setup, teardown):
        with listen_for_interrupt():
            if interval:
                repeat_on_schedule(loop, interval)
            else:
                repeat(loop)

# alias 
def run_loop(*args, **kwargs):
    """See tuppersat.utils.scriptutils.run."""
    return run(*args, **kwargs)


# ****************************************************************************
# command line argument configuration toolkit
# ****************************************************************************

def wait_for_interrupt(callback=None):
    """Block until KeyboardInterrupt received."""
    with listen_for_interrupt(callback):
        repeat(time.sleep, 5)
    return


# ****************************************************************************
# command line argument configuration toolkit
# ****************************************************************************

def configure_argument_parser(description="", arguments=None):
    """Create a command line argument handler from list of allowed options.
    
    The arguments should be provided as a list of tuples containing the
    argument name and dictionaries with any additional keyword arguments to be
    given to ArgumentParser.add_argument.

    """
    import argparse

    # TODO: what is the correct behaviour if there are no arguments to pass?
    if arguments is None:
        arguments = []
    
    parser = argparse.ArgumentParser(description=description)

    for *opt, opt_kwargs in arguments:
        parser.add_argument(*opt, **opt_kwargs)

    return parser

# ****************************************************************************
# default filename function
# ****************************************************************************

def timestamped_filename(name=None, ext='.dat', datefmt='%Y-%m-%d-%H%M%S'):
    """A convenience function for creating filenames with timestamps.

    Parameters
    ==========
    name : [optional]
        the filename

    ext : [optional]
        the file extension. Default is .dat

    datefmt : [optional]
        the date format (see datetime for details). Default YYYY-mm-dd-HHMMSS

    """
    _timestamp = f"{dt.datetime.now():{datefmt}}"
    _name = (f"-{name}" if name else "")
    _ext = (f".{ext}" if not ext.startswith(".") else ext)
    return f"{_timestamp}{_name}{_ext}"
