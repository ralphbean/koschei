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
from __future__ import print_function

import sys
import logging

if __name__ != '__main__':
    print("This module shall not be imported", file=sys.stderr)
    sys.exit(2)

from .service import Service

# Importing all modules that define services
# pylint: disable=W0611
from . import util, scheduler, resolver, polling, watcher, plugin

log = logging.getLogger('koschei.main')

if len(sys.argv) < 2:
    print("Requires service name", file=sys.stderr)
    sys.exit(2)
name = sys.argv[1]
plugin.load_plugins()
service = Service.find_service(name)
if not service:
    print("No such service", file=sys.stderr)
    sys.exit(2)
try:
    service().run_service()
except Exception as exc:
    log.error("Service {} crashed: {}: {}"
              .format(name, type(exc), exc))
    raise
