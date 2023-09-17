#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Fabrice Luo <fabriceluo@outlook.com>
#
# Distributed under terms of the MIT license.

"""
便利的文件对象封装
"""
import os


class File(object):
    def __init__(self, root, rpath, repo=None):
        self._root = root
        self._repo = repo
        self._rpath = rpath

        self._apath = os.path.join(root, rpath)
        self._dirname = os.path.dirname(self._apath)
        self._filename = os.path.basename(rpath)

    @property
    def name(self):
        return self._filename

    @property
    def dirname(self):
        return self._dirname

    @property
    def abs_path(self):
        return self._apath

    @property
    def repo(self):
        return self._repo

    @property
    def content(self):
        # 每次都读取最新的文件
        with open(self._apath) as fp:
            return fp.readlines()
