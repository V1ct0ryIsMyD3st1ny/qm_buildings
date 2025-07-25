from functools import wraps

def lazy_init(f):
    """Wrapper to call the function once and cache the result"""
    initialized = False
    result = None
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        nonlocal initialized, result
        if not initialized:
            result = f(*args, **kwargs)
            initialized = True
        return result
    
    return wrapper