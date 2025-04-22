import time
import os
from telegram.ext import ContextTypes

CACHE = {}
EXPIRY = int(os.getenv("CACHE_EXPIRY", 300))

def simple_cache(expiry: int = EXPIRY):
    def decorator(fn):
        async def wrapper(*args, **kwargs):
            key = (fn.__name__, args, frozenset(kwargs.items()))
            now = time.time()
            if key in CACHE and now - CACHE[key][0] < expiry:
                return CACHE[key][1]
            res = await fn(*args, **kwargs)
            CACHE[key] = (now, res)
            return res
        return wrapper
    return decorator

async def cleanup_cache(context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    keys = [k for k, (t, _) in CACHE.items() if now - t > EXPIRY]
    for k in keys:
        del CACHE[k]
