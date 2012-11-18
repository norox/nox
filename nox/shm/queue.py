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

'''The ``nox.shm.queue`` packages contains a shared memory queue'''

__author__ = 'Stefan Andersson'
__license__ = 'LGPL'
__all__ = ['Queue', 'Empty', 'Full', 'NotSupported']

import ctypes
from multiprocessing import Value, Lock

class Empty(Exception):
    message = 'queue is empty'

class Full(Exception):
    message = 'queue is full'

class NotSupported(Exception):
    message = 'qsize not supported on un-synchronization'

def Queue(_type, size, lock = False):
    '''
    A shared memory queue with and without synchronization
    :param _type: ctypes.c_type or ctypes.Structure
    :param size: Size of the queue
    :param lock: Synchronized (default: False)
    :return: Queue or SynchronizedQueue
    '''
    class Item(ctypes.Structure):
        def is_used(self):
            return self._used

        def set(self, _type):
            try:
                self._type.from_python(_type)
            except AttributeError:
                self._type = _type

            self._used = True

        def get(self):
            try:
                data = self._type.to_python()
            except AttributeError:
                if isinstance(self._type, ctypes.Structure):
                    data = type(self._type).from_buffer_copy(self._type)
                else:
                    data = type(self._type)(self._type)

            self._used = False
            return data

    Item._fields_ = [
        ('_used', ctypes.c_bool),
        ('_type', _type)
    ]

    class Queue(ctypes.Structure):
        def __init__(self, size):
            self._size = size
            self.clear()

        def clear(self):
            self._next_read = 0
            self._next_free = 0
            ctypes.memset(self._queue, 0, ctypes.sizeof(self._queue))

        def put(self, _type):
            n = self._next_free
            if self._queue[n].is_used():
                raise Full
            else:
                self._queue[n].set(_type)
                self._next_free = (n + 1) % self._size

        def get(self):
            n = self._next_read
            if not self._queue[n].is_used():
                raise Empty
            self._next_read = (n + 1) % self._size
            return self._queue[n].get()

        def qsize(self):
            raise NotSupported()

    Queue._fields_ = [
        ('_next_read', ctypes.c_uint),
        ('_next_free', ctypes.c_uint),
        ('_size', ctypes.c_uint),
        ('_queue', Item * size)
    ]

    class SynchronizedQueue(Queue):
        def __init__(self, size):
            self._wlock = Lock()
            self._rlock = Lock()
            super(SynchronizedQueue, self).__init__(size)

        def put(self, _type):
            self._wlock.acquire()
            try:
                super(SynchronizedQueue, self).put(_type)
            finally:
                self._wlock.release()

        def get(self):
            self._rlock.acquire()
            try:
                return super(SynchronizedQueue, self).get()
            finally:
                self._rlock.release()

        def qsize(self):
            self._wlock.acquire()
            self._rlock.acquire()
            try:
                next_free = self._next_free
                next_read = self._next_read
                if next_free == next_read:
                    if self._queue[next_read].is_used():
                        return size # Full
                    else:
                        return 0L # Empty
                else:
                    if next_free > next_read:
                        return next_free - next_read
                    else:
                        return self._size + next_free - next_read
            finally:
                self._wlock.release()
                self._rlock.release()

    if lock:
        return Value(SynchronizedQueue, size, lock = False)
    else:
        return Value(Queue, size, lock = False)
