================
Cache attributes
================

Description
===========

Cleaning Cache
--------------

``kids.cache`` uses some ``lru_cache`` ideas of python 3
implementation, and each function cached received a ``cache_clear``
method::

    >>> from kids.cache import cache

    >>> @cache
    ... def mysum(*args):
    ...     print("calculate...")
    ...     return sum(args)

    >>> mysum(1,1)
    calculate...
    2
    >>> mysum(1,1)
    2

By calling ``cache_clear`` method, we flush all previous cached value::

    >>> mysum.cache_clear()
    >>> mysum(1,1)
    calculate...
    2


Cache stats
-----------

``kids.cache`` uses some ``lru_cache`` ideas of python 3
implementation, and each function cached received a ``cache_info``
method::

    >>> @cache
    ... def mysum(*args):
    ...     print("calculate...")
    ...     return sum(args)

    >>> mysum(1,1)
    calculate...
    2
    >>> mysum(1,1)
    2

    >>> mysum.cache_info()
    CacheInfo(type='dict', hits=1, misses=1, maxsize=None, currsize=1)


Access
======

Access to the ``cache_info`` attribute is straightforward...

for functionm::

    >>> @cache
    ... def fun(): pass

    >>> fun.cache_info
    <function ...cache_info...>

for class::

    >>> @cache
    ... class MyObject(object): pass

    >>> MyObject.cache_info
    <function ...cache_info...>

for method, classmethod, staticmethod::

    >>> class MyObject(object):
    ...
    ...    @cache
    ...    def meth(self): pass
    ...
    ...    @classmethod
    ...    @cache
    ...    def clsmeth1(cls): pass
    ...
    ...    @cache
    ...    @classmethod
    ...    def clsmeth2(cls): pass
    ...
    ...    @staticmethod
    ...    @cache
    ...    def stmeth1(): pass
    ...
    ...    @cache
    ...    @staticmethod
    ...    def stmeth2(): pass

    >>> xx = MyObject()

    >>> xx.meth.cache_info
    <function ...cache_info...>

    >>> xx.clsmeth1.cache_info
    <function ...cache_info...>

    >>> xx.clsmeth2.cache_info
    <function ...cache_info...>

    >>> xx.stmeth1.cache_info
    <function ...cache_info...>

    >>> xx.stmeth2.cache_info
    <function ...cache_info...>


But it's a little tricky for properties::

    >>> class WithProperty(MyObject):
    ...
    ...    def __init__(self, a, b):
    ...        self.a = a
    ...        self.b = b
    ...
    ...    @property
    ...    @cache
    ...    def total(self):
    ...        return self.a + self.b

    >>> xx = WithProperty(1, 1)

As you can understand, you won't be able to access the ``cache_info``
easily and you might want to see it::

    >>> xx.total.cache_info
    Traceback (most recent call last):
    ...
    AttributeError: 'int' object has no attribute 'cache_info'

You need too access the property object, which is in the class object::

    >>> WithProperty.total
    <property object at ...>

But you won't be able to access cache_info directly::

    >>> WithProperty.total.cache_info
    Traceback (most recent call last):
    ...
    AttributeError: 'property' object has no attribute 'cache_info'

The best way could be to use the ``undecorate`` function of ``kids.cache``::

    >>> from kids.cache import undecorate
    >>> undecorate(WithProperty.total)
    (<... 'property'>, <function ...total at ...>)

The second element is the pristine function that holds the correct attribute::

    >>> undecorate(WithProperty.total)[1].cache_info
    <function ...cache_info...>


The same procedure works with ``@property`` and ``@cache`` inverted::

    >>> class WithProperty(MyObject):
    ...
    ...    def __init__(self, a, b):
    ...        self.a = a
    ...        self.b = b
    ...
    ...    @cache
    ...    @property
    ...    def total(self):
    ...        return self.a + self.b

The same procedure will work::

    >>> undecorate(WithProperty.total)[1].cache_info
    <function ...cache_info...>



