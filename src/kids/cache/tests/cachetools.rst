
Some ``cachetools`` cache can cast a ``ValueError`` exception when
assigning a new entry.

``kids.cache`` then purposedly ignores it. And the value don't get
cached then.

    >>> from kids.cache import cache
    >>> from cachetools import LRUCache

    >>> cachestore = LRUCache(maxsize=0)
    >>> @cache(use=cachestore)
    ... def mysum(*args):
    ...     print("calculate...")
    ...     return sum(args)

    >>> mysum(1, 1)
    calculate...
    2
    >>> mysum(1, 1)
    calculate...
    2

As we can see, nothing is stored in this cachestore. This is because::

    >>> cachestore["new entry"] = "a value"
    Traceback (most recent call last):
    ...
    ValueError: value too large

