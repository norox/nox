# -*- coding: utf8 -*-
# One producer and two consumer, you could have multiple producers and consumers
from multiprocessing import Process, Event
from time import time, sleep
from os import path
import sys, ctypes

sys.path.extend(['/'.join(path.realpath(path.dirname(sys.argv[0])).split('/')[:-1])])

from nox.shm import Queue, Empty, Full

if __name__ == '__main__':
    class Data(ctypes.Structure):
        _fields_ = [
            ('length', ctypes.c_uint),
            ('data', ctypes.c_byte * 64)
        ]

        def from_python(self, data):
            length = len(data)
            ctypes.memmove(self.data, (ctypes.c_byte * length).from_buffer(bytearray(data)), ctypes.sizeof(self.data))
            self.length = length

        def to_python(self):
            return str(bytearray(self.data[:self.length]))

    size = 100000
    q = Queue(Data, size, True) # True makes the queue synchronized
    run = Event()
    run.set()

    def worker(q, r):
        while r.is_set():
            try:
                v = q.get()
                assert(v.startswith('test'))
                sleep(0.00001)
            except Empty:
                pass

    def main(q):
        v = 0
        t = time()
        while v != (size * 3):
            try:
                if time() - t > 0.4:
                    print 'Queue.qsize:', q.qsize()
                    t = time()
                q.put('test' + str(v))
                v += 1
            except Full:
                pass

    s = time()
    p1 = Process(target = worker, args=(q, run))
    p1.start()
    p2 = Process(target = worker, args=(q, run))
    p2.start()

    main(q)
    qs = q.qsize()
    while qs > 0:
        print 'Queue.qsize:', qs
        sleep(0.4)
        qs = q.qsize()
    run.clear()

    p1.join()
    p2.join()
    print 'nox.shm.Queue put/get: %s' %(time() - s)
