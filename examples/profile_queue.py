# -*- coding: utf8 -*-
# Use the profile decorator to profile two threads/processes
# Use runsnake main.prof worker.prof after to see the profiling
from multiprocessing import Process
from time import time
from os import path
import sys, ctypes

sys.path.extend(['/'.join(path.realpath(path.dirname(sys.argv[0])).split('/')[:-1])])

from nox.shm import Queue, Empty, Full
from nox.decorator import profile

if __name__ == '__main__':
    class Data(ctypes.Structure):
        _fields_ = [
            ('length', ctypes.c_uint),
            ('data', ctypes.c_byte * 1024)
        ]

        def from_python(self, data):
            length = len(data)
            ctypes.memmove(self.data, (ctypes.c_byte * length).from_buffer(bytearray(data)), ctypes.sizeof(self.data))
            self.length = length

        def to_python(self):
            return str(bytearray(self.data[:self.length]))

    size = 1000
    q = Queue(Data, size, False) # False makes the queue un-synchronized

    @profile('worker.prof')
    def worker(q, s):
        c = 0
        while c != s:
            try:
                v = q.get()
                assert(v == ('test' + str(c)) * ((c % 10) + 1))
                c += 1
            except Empty:
                pass
            except Exception, e:
                print v, c
                raise

    @profile('main.prof')
    def main(q):
        v = 0
        while v != (size * 1000):
            try:
                q.put(('test' + str(v)) * ((v % 10) + 1))
                v += 1
            except Full:
                pass

    s = time()
    p = Process(target = worker, args=(q, size * 1000))
    p.start()

    main(q)

    p.join()
    print 'nox.shm.Queue put/get: %s' %(time() - s)
