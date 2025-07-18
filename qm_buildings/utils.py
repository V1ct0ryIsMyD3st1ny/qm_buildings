def lazy_init(func):
    """Wrapper to call the function once and cache the result"""
    initialized = False
    result = None
    
    def wrapper(*args, **kwargs):
        nonlocal initialized, result
        if not initialized:
            result = func(*args, **kwargs)
            initialized = True
        return result
    
    return wrapper

