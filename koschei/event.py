# Copyright (C) 2014  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author: Michael Simacek <msimacek@redhat.com>


class Event(object):
    """ Base for events """

    listeners = []

    @classmethod
    def listen(cls, fn):
        cls.listeners.append(fn)
        return fn

    def dispatch(self):
        for listener in self.listeners:
            listener(self)


class EventQueue(object):

    def __init__(self):
        self._queue = []

    def add(self, event):
        self._queue.append(event)

    def flush(self):
        for event in self._queue:
            event.dispatch()
        self._queue = []

    def rollback(self):
        self._queue = []

    def empty(self):
        return not self._queue
