#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Fabrice Luo <fabriceluo@outlook.com>
#
# Distributed under terms of the MIT license.

"""
监控文件的变更并通知
"""

from watchdog import events
from utils import get_git_root
from utils import get_git_repo
from file import File

import logging

LOG = logging.getLogger()


class CodeEventHandler(events.PatternMatchingEventHandler):
    def __init__(self,
                 root,
                 repo,
                 session,
                 finders,
                 patterns=None,
                 ignore_patterns='.git',
                 ignore_directories=True,
                 case_sensitive=True,
                 ):
        super.__init__(self,
                       patterns=patterns,
                       ignore_patterns=ignore_regexes,
                       ignore_directories=ignore_directories,
                       case_sensitive=case_sensitive)

        self._root = root
        self._repo = repo
        self._session = session
        self._finders = finders

    def on_modified(self, event):
        if not isinstance(event, events.FileModifiedEvent):
            return

        apath = event.src_path
        rpath = apath.replace(self._root, '')

        file = File(self.root, rpath, self._repo)
        self.sync(file)

    def sync(self, file):
        for finder in self._finders:
            remote_path = finder.find(file)

            if remote_path:
                break
            pass

        if not remote_path:
            LOG.warning("remote path for file(%s) is not found", file)
            return

        LOG.info("sync file local(%s) to remote(%s)",
                 file.abs_path, remote_path)
        self._session.put(file.abs_path, remote_path)
