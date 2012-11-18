# -*- coding: utf8 -*-
#
# nox - Copyright (C) nox contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

__author__ = 'Stefan Andersson'
__license__ = 'LGPL'
__all__ = ['synchronized']

from multiprocessing import Lock

def synchronized(lock = None):
    '''
    Use this decorator to make a function thread-safe that is otherwise not.
    If no lock is supplied one will be created.
    :param lock: ``threading.Lock`` or ``multiprocessing.Lock``
    '''
    if not lock:
        lock = Lock()

    def inner(func):
        def wrapper(*args, **kwargs):
            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()
        return wrapper
    return inner
