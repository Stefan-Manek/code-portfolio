"""
contextutils.py

Convenience tools relating to context-like patterns.
"""
# standard library imports
import contextlib


# ****************************************************************************

class ContextStack:
    def __init__(self, contexts):
        self._contexts = contexts
        self._exitstack = None

    # TODO: custom __repr__?
        
    def __enter__(self):
        return self.enter()
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.exit()
        return False

        
    def enter(self):
        """Safely enter all contexts in the stack."""
        with contextlib.ExitStack() as cm:
            contexts = [cm.enter_context(c) for c in self._contexts]
            self._exitstack = cm.pop_all()
        return contexts
        
    def exit(self):
        """Safely exit all contexts in the open stack."""
        return self._exitstack.close()


# ****************************************************************************

class SetupStack(ContextStack):
    """A ContextStack for objects with setup and teardown methods."""
    def enter(self):
        """Safely setup all objects in the stack."""
        # function to link object to context manager  
        def _setup(obj, cm):
            obj.setup()
            cm.callback(obj.teardown)
            return obj 

        with contextlib.ExitStack() as cm:
            contexts = [_setup(c, cm) for c in self._contexts]
            self._exitstack = cm.pop_all()
        return contexts

# ****************************************************************************


@contextlib.contextmanager
def NoContext():
    """A context manager that does nothing!
    
    (cf contextlib.nullcontext in python37 and later)
    """
    yield None

@contextlib.contextmanager
def OptionalContext(cm):
    """Wrapper to make a context optional by passing None in its place."""
    with (cm if cm else NoContext()) as _cm:
        yield _cm
