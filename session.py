#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Fabrice Luo <fabriceluo@outlook.com>
#
# Distributed under terms of the MIT license.

"""
维护远程会话，封装常见操作
"""
from fabric import Connection


class Session(object):
    def __init__(self, roots, host, port, username, password):
        self._roots = roots

        connect_kwargs = {
            'port': port,
            'username': username,
            'password': password,
        }
        self._session = Connection(host, connect_kwargs=connect_kwargs)

    def put(self, local, remote):
        self._session.put(local, remote)

    def get(self, local, remote):
        self._session.get(remote, local)

    def find_files(self, root):
        cmds = ['find', root, '-type', 'f']
        cmd_str = ' '.join(cmds)

        result = self._session.run(cmd_str)
        if result.exited != 0:
            raise RuntimeError('run cmd:%s failed, out:%s, err:%s' %
                               (result.command, result.stdout, result.stderr))

        files = result.stdout.splitlines()
        return files

    def run(self, *args, **kwargs):
        self._session.run(*args, **kwargs)

    @property
    def roots(self):
        self._roots
