# Package placeholder

import threading
import functools
import collections


CacheInfo = collections.namedtuple(
    'CacheInfo', 'type hits misses maxsize currsize')


def make_key(obj, typed=True):
    args, kwargs = obj
    key = (tuple(args), tuple(sorted(kwargs.items())))
    if typed:
        key += tuple(type(v) for v in args)
        key += tuple(type(v) for _, v in sorted(kwargs.items()))
    return key


def is_hashable(obj):
    try:
        hash(obj)
        return True
    except Exception:  ## pylint: disable-msg=W0703
        return False


def make_key_hippie(obj, typed=True):
    """Return hashable structure from non-hashable structure using hippie means

    dict and set are sorted and their content subjected to same hippie means.

    Note that the key identifies the current content of the structure.

    """
    ftype = type if typed else lambda o: None
    if is_hashable(obj):
        ## DO NOT RETURN hash(obj), as hash collision would generate bad
        ## cache collisions.
        return obj, ftype(obj)
    ## should we try to convert to frozen{set,dict} to get the C
    ## hashing function speed ? But the convertion has a cost also.
    if isinstance(obj, set):
        obj = sorted(obj)
    if isinstance(obj, (list, tuple)):
        return tuple(make_key_hippie(e, typed) for e in obj)
    if isinstance(obj, dict):
        return tuple(sorted(((make_key_hippie(k, typed),
                              make_key_hippie(v, typed))
                             for k, v in obj.items())))
    raise ValueError(
        "%r can not be hashed. Try providing a custom key function."
        % obj)


def hashing(typed=True, strict=False):
    """Returns a typed and/or strict key callable.

    A strict key callable will fail on traditionaly non-hashable object,
    while a strict=False hashing will use hippie hashing that can hash
    mutable object.

    A typed key callable will use type of each object in the hash and will
    distinguish with same hash but different type (example: 2 and 2.0).

    """
    hashable_struct_producer = make_key if strict else make_key_hippie

    def _make_key(*args, **kwargs):
        ## use a list to avoid using hash of tuples...
        return hashable_struct_producer([list(args), kwargs], typed=typed)
    return _make_key


SUPPORTED_DECORATOR = {
    property: lambda f: f.fget,
    classmethod: lambda f: f.__func__,
    staticmethod: lambda f: f.__func__,
}

def undecorate(func):
    """Returns the decorator and the undecorated function of given object."""
    orig_call_wrapper = lambda x: x
    for call_wrapper, unwrap in SUPPORTED_DECORATOR.items():
        if isinstance(func, call_wrapper):
            func = unwrap(func)
            orig_call_wrapper = call_wrapper
            break
    return orig_call_wrapper, func


## inspired by cachetools.decorators.cachedfunc
def cachedfunc(cache_store, key=make_key_hippie):
    context = threading.RLock()  ## stats lock

    def decorator(func):
        stats = [0, 0]

        wrapper, wrapped = undecorate(func)

        @functools.wraps(wrapped)
        def _cache_wrapper(*args, **kwargs):
            k = key(*args, **kwargs)
            with context:
                try:
                    result = cache_store[k]
                    stats[0] += 1
                    return result
                except KeyError:
                    stats[1] += 1
            result = wrapped(*args, **kwargs)
            with context:
                try:
                    cache_store[k] = result
                except ValueError:
                    ## Value 'too large', only casted with cachetools stores.
                    pass
            return result

        ## mimic's python3 ``lru_cache`` facilities.

        def cache_info():
            with context:
                hits, misses = stats
                maxsize = getattr(cache_store, "maxsize", None)
                currsize = getattr(cache_store, "currsize", len(cache_store))
            return CacheInfo(
                type(cache_store).__name__, hits, misses, maxsize, currsize)

        def cache_clear():
            with context:
                cache_store.clear()

        _cache_wrapper.cache_info = cache_info
        _cache_wrapper.cache_clear = cache_clear

        return wrapper(_cache_wrapper)

    return decorator


def cache(*args, **kwargs):
    """The @cache decorator

    Compatility with using ``@cache()`` and ``@cache`` is managed in
    the current function.

    """
    ## only one argument ?
    if len(args) == 1 and len(kwargs) == 0 and \
           (callable(args[0]) or \
            isinstance(args[0], tuple(SUPPORTED_DECORATOR.keys()))):
        return _cache_w_args(args[0])
    return lambda f: _cache_w_args(f, *args, **kwargs)


## No locking mecanism because this should be implemented in the Cache
## objects if needed.
def _cache_w_args(f, use=None, cache_factory=dict,
                  key=None, strict=False, typed=False):
    if key is None:
        key = hashing(strict=strict, typed=typed)
    if use is None:
        use = cache_factory()
    return cachedfunc(cache_store=use, key=key)(f)


hippie_hashing = hashing()
