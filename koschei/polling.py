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

import koji

from sqlalchemy.sql import exists

from . import util
from .models import Build, RepoGenerationRequest
from .service import KojiService
from .backend import Backend

build_tag = util.koji_config['build_tag']


class Polling(KojiService):
    def __init__(self, backend=None, *args, **kwargs):
        super(Polling, self).__init__(*args, **kwargs)
        self.backend = backend or Backend(log=self.log, db=self.db,
                                          koji_session=self.koji_session)

    def poll_builds(self):
        running_builds = self.db.query(Build)\
                                .filter_by(state=Build.RUNNING)
        for build in running_builds:
            name = build.package.name
            if not build.task_id:
                self.log.warn('No task id assigned to build {0})'
                              .format(build))
            else:
                task_info = self.koji_session.getTaskInfo(build.task_id)
                self.log.debug('Polling task {id} ({name}): task_info={info}'
                               .format(id=build.task_id, name=name,
                                       info=task_info))
                state = koji.TASK_STATES.getvalue(task_info['state'])
                self.backend.update_build_state(build, state)

    def poll_repo(self):
        curr_repo = self.koji_session.getRepo(build_tag, state=koji.REPO_READY)
        if curr_repo:
            if not self.db.query(exists()
                                 .where(RepoGenerationRequest.repo_id
                                        == curr_repo['id'])).scalar():
                request = RepoGenerationRequest(repo_id=curr_repo['id'])
                self.db.add(request)
                self.db.commit()

    def main(self):
        self.poll_builds()
        self.poll_repo()
