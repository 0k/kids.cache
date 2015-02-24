==========
kids.cache
==========


.. image:: http://img.shields.io/pypi/v/kids.cache.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.cache/
   :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/kids.cache.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.cache/
   :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/0k/kids.cache/master.svg?style=flat
   :target: https://travis-ci.org/0k/kids.cache/
   :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/0k/kids.cache/master.svg?style=flat
   :target: https://coveralls.io/r/0k/kids.cache
   :alt: Test coverage


``kids.cache`` is a Python library providing a cache decorator.
It's part of 'Kids' (for Keep It Dead Simple) library.

It main concern is to offer a very simple default usage.
Without forgetting to offer power inside when needed.


Maturity
========

This code is in alpha stage.


Compatibility
=============

This code is tested for compatibility with python 2.7 and python >= 3 .


Features
========

using ``kids.cache``:

- Use one simple call to ``@cache``, and a majority of all hidden complexity
  will vanish.

  - works out of the box on function, methods, property.
  - support to be called before or after @property.

- Or go deeper into customization:

  - cache clearing functionality
  - cache stats
  - support of any cache store mecanism from `cachetools`_ package
  - support of custom key function which allows:

    - support of your exotic unhashable objects
    - fine tune what function calls should be considered identic
    - hand pick function dependencies in object (for method)


.. _cachetools: https://github.com/tkem/cachetools

Basic Usage
===========

Function
--------

This cache decorator is quite straightforward to use::

    >>> from kids.cache import cache

    >>> @cache
    ... def answer_to_everything():
    ...     print("many insightfull calculation")
    ...     return 42

Then the function ``answer_to_everything`` would only do the
calculation the first time called, and would save the result, and
directly return it the next calls::

    >>> answer_to_everything()
    many insightfull calculation
    42

    >>> answer_to_everything()
    42

The body of the function was not executed anymore and the cache value
was used.

It'll work with arguments::

    >>> @cache
    ... def mysum(*args):
    ...     print("calculating...")
    ...     return sum(args)

    >>> mysum(2, 2, 3)
    calculating...
    7
    >>> mysum(1, 1, 1, 1)
    calculating...
    4
    >>> mysum(2, 2, 3)
    7
    >>> mysum(1, 1, 1, 1)
    4

And notice that by default, object are not typed, thus::

    >>> mysum(1.0, 1, 1, 1)
    4

Did trigger the cache, despite the first argument is a float and not
an integer.


Methods
-------

With methods::

    >>> class MyObject(object):
    ...    def __init__(self, a, b):
    ...        self.a, self.b = a, b
    ...
    ...    @cache
    ...    def total(self):
    ...        print("calculating...")
    ...        return self.a + self.b

    >>> xx = MyObject(2, 3)
    >>> xx.total()
    calculating...
    5
    >>> xx.total()
    5

Cache is not shared between instances::

    >>> yy = MyObject(2, 3)
    >>> yy.total()
    calculating...
    5

Of course, if you change the inner values of the instance, this
will NOT be detected by the caching method::

    >>> xx.a = 5
    >>> xx.total()
    5

Look at advanced usages to see how to changes some of these behaviors.


Property
--------

You can use the ``cache`` decorator with properties, and
provides a good way to have lazy evaluated attributes::

    >>> class WithProperty(MyObject):
    ...
    ...    @property
    ...    @cache
    ...    def total(self):
    ...        print("evaluating...")
    ...        return self.a + self.b

    >>> xx = WithProperty(1, 1)
    >>> xx.total
    evaluating...
    2
    >>> xx.total
    2

You can use ``@cache`` decorator before or after ``@property``
decorator::

    >>> class WithProperty(MyObject):
    ...
    ...    @cache
    ...    @property
    ...    def total(self):
    ...        print("evaluating...")
    ...        return self.a + self.b

    >>> xx = WithProperty(2, 2)
    >>> xx.total
    evaluating...
    4
    >>> xx.total
    4


Advanced Usage
==============

Most of the advanced usage implies to call the ``@cache`` decorator with
arguments. Please notice that::

    >>> @cache
    ... def mysum1(*args):
    ...     print("calculating...")
    ...     return sum(args)

Or::

    >>> @cache()
    ... def mysum2(*args):
    ...     print("calculating...")
    ...     return sum(args)

is equivalent::

    >>> mysum1(1,1)
    calculating...
    2
    >>> mysum1(1,1)
    2

    >>> mysum2(1,1)
    calculating...
    2
    >>> mysum2(1,1)
    2


Provide a key function
----------------------

Providing a key function can be extremely powerfull and will allow to
fine tune when the cache should be recalculated.

``hashing`` functions will receive exactly the same arguments than the
main function called. It must return an hashable structure
(combination of ``tuples``, ``int``, ``string``... avoid list and
dicts). This will identify uniquely the result.

For example you could::

    >>> class WithKey(MyObject):
    ...    @cache(key=lambda s: (id(s), s.a, s.b))
    ...    def total(self):
    ...        print("calculating...")
    ...        return self.a + self.b

    >>> xx = WithKey(2, 3)
    >>> xx.total()
    calculating...
    5
    >>> xx.total()
    5

It should detect changes of the given values of the instance::

    >>> xx.a = 5
    >>> xx.total()
    calculating...
    8

Without bothering to recalculate when other values change::

    >>> xx.c = 7
    >>> xx.total()
    8

But it should make a difference between instances::

    >>> yy = WithKey(2, 3)
    >>> yy.total()
    calculating...
    5


Typed key functions
-------------------

You could ask for ``typed`` argument to NOT be treated the same::

    >>> @cache(typed=True)
    ... def mysum(*args):
    ...     print("calculating...")
    ...     return sum(args)
    >>> mysum(1, 1)
    calculating...
    2

    >>> mysum(1.0, 1)
    calculating...
    2.0


Key functions
-------------

The default key function if not provided is a bold try to make ``list``
and ``dict`` also keyable despite these not being hashable.

The name of the key function is called ``hippie_hashing``, and this is
the default value for the key argument::

    >>> from kids.cache import hippie_hashing

    >>> @cache(key=hippie_hashing)
    ... def mylength(obj):
    ...     return len(obj)

This allows you to use the function with list, dict or combination of these::

    >>> mylength([3, 2, 1])
    3

Even your objects could be used as key, as long as they are hashable::

    >>> class MyObj(object):  ## object subclasses have a default hash
    ...     length = 5
    ...     def __len__(self, ):
    ...         print('calculating...')
    ...         return self.length

    >>> myobj = MyObj()
    >>> mylength(myobj)
    calculating...
    5

    >>> mylength(myobj)
    5

Be assured that hash collision (they happen!) won't generate cache collisions::

    >>> class MyCollidingHashObj(MyObj):
    ...     def __init__(self, length):
    ...          self.length = length
    ...     def __hash__(self):
    ...          return 1

    >>> hash_collide1 = MyCollidingHashObj(6)
    >>> hash_collide2 = MyCollidingHashObj(7)

    >>> mylength(hash_collide1)
    calculating...
    6
    >>> mylength(hash_collide2)
    calculating...
    7

But try to avoid them for performance's sake !! And you should
probably be aware that if your object compare equal, then THERE WILL
BE a cache collision (but at this point, this is probably what you
wanted, heh ?)::

    >>> class MyEqCollidingHashObj(MyCollidingHashObj):
    ...     def __eq__(self, value):
    ...          return True
    ...     def __hash__(self):
    ...          return 1

    >>> eq_and_hash_collide1 = MyEqCollidingHashObj(8)
    >>> eq_and_hash_collide2 = MyEqCollidingHashObj(9)

    >>> mylength(eq_and_hash_collide1)
    calculating...
    8
    >>> mylength(eq_and_hash_collide2)
    8

Huh oh. This is not what was probably expected in this example, but
you really had to work hard to make this happen. And most of the time,
you'll probably find this convenient and will use it at you advantage.
It's a little bit like an extension of the ``key`` mecanism that is
the objects responsability.

.. note:: Please verify also that if your object compares the same, their
  hash HAS TO BE the same. For this very reason, in Python3, when you
  define the ``__eq__`` method, it'll remove the default ``__hash__``
  from objects.


Of course, ``hippie_hashing`` will fail on special unhashable object::

    >>> class Unhashable(object):
    ...    def __hash__(self):
    ...        raise ValueError("unhashable!")

    >>> hippie_hashing(Unhashable())  ## doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: <Unhashable ...> can not be hashed. Try providing a custom key function.

If you are not a hippie, you should consider using ``strict=True`` and a
much more limited by sober method will be used to make a key from your
arguments::

    >>> @cache(strict=True)
    ... def mylength(obj):
    ...     return len(obj)

    >>> mylength("hello")
    5

But then, don't be surprised if it fails with dict, list, or set arguments::

    >>> mylength([3, 2, 1])
    Traceback (most recent call last):
    ...
    TypeError: unhashable type: 'list'


And ``typed=True`` can be used in combination with ``strict=True``::

    >>> @cache(strict=True, typed=True)
    ... def mysum(*args):
    ...     print("calculating...")
    ...     return sum(args)
    >>> mysum(1, 1)
    calculating...
    2

    >>> mysum(1.0, 1)
    calculating...
    2.0

A good key function can:

- make some cache timeout (but you should then look at cache store
  section to limit the size of the cache)
- finely select which argument are pertinent to the method.
- allow you to cache callables that have very special arguments that
  can't be hashed properly.


Cleaning Cache
--------------

``kids.cache`` uses some ``lru_cache`` ideas of python 3
implementation, and each function cached received a ``cache_clear``
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


Cache Store
-----------

``kids.cache`` can use any dict-like structure as a cache store. This
means you can provide some more clever cache stores. For example, you
can use ``cachetools`` caches under the hood to manage the caching store.

Keep in mind that the default cache store is... a dict ! which is not
a good idea if your program will run for a long time.

So if you need any caching store from ``cachetools`` you can provide
it::

    >>> from cachetools import LRUCache

LRU stands for Least Recent Used... ::

    >>> @cache(use=LRUCache(maxsize=2))
    ... def mysum(*args):
    ...     print("calculate...")
    ...     return sum(args)

    >>> mysum(1, 1)
    calculate...
    2
    >>> mysum(1, 2)
    calculate...
    3
    >>> mysum(1, 3)
    calculate...
    4

We have exceeded the cache memory and the least recent used have been
tossed away::

    >>> mysum(1, 1)
    calculate...
    2

But we still have this one in memory::

    >>> mysum(1, 3)
    4


Contributing
============

Any suggestion or issue is welcome. Push request are very welcome,
please check out the guidelines.


Push Request Guidelines
-----------------------

You can send any code. I'll look at it and will integrate it myself in
the code base and leave you as the author. This process can take time and
it'll take less time if you follow the following guidelines:

- check your code with PEP8 or pylint. Try to stick to 80 columns wide.
- separate your commits per smallest concern.
- each commit should pass the tests (to allow easy bisect)
- each functionality/bugfix commit should contain the code, tests,
  and doc.
- prior minor commit with typographic or code cosmetic changes are
  very welcome. These should be tagged in their commit summary with
  ``!minor``.
- the commit message should follow gitchangelog rules (check the git
  log to get examples)
- if the commit fixes an issue or finished the implementation of a
  feature, please mention it in the summary.

If you have some questions about guidelines which is not answered here,
please check the current ``git log``, you might find previous commit that
would show you how to deal with your issue.


License
=======

Copyright (c) 2015 Valentin Lab.

Licensed under the `BSD License`_.

.. _BSD License: http://raw.github.com/0k/kids.cache/master/LICENSE

