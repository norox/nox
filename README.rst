About
=====

Nox library are some helpful function and classes that I found useful to have in a separate package
so they can be reused in different projects.

Requirements
============

Nox library works with any version of Python 2.5 through 2.7.
It has not been tested with version 3.0 or newer.

Content
=======

 * ``nox.decorator.profile`` a decorator that uses cProfile, helpful when profiling ``multiprocessing.Process``.
 * ``nox.decorator.synchronized`` synchronize access to a function or a group of functions.
 * ``nox.shm.Queue`` shared memory queue, useful when using ``multiprocessing`` library,
   when using only one producer and consumer you don't need to use lock = True, if you want to use multiple producers
   and/or consumers set it to True.
 * ``nox.sqlalchemy.get_compiled_query`` a function for debugging purpose only, give it a query statement and it will
   return a query string.
