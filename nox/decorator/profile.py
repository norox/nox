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
__all__ = ['profile']

import cProfile

def profile(name):
    '''
    Use this decorator on the main entry point
    of the application to profile it.
    :param name: Name of the profile dump
    '''
    def inner(func):
        def wrapper(*args, **kwargs):
            prof = cProfile.Profile()
            ret = prof.runcall(func, *args, **kwargs)
            prof.dump_stats(name)
            return ret
        return wrapper
    return inner
