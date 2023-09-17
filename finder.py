#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Fabrice Luo <fabriceluo@outlook.com>
#
# Distributed under terms of the MIT license.

"""
获取同步文件的目的位置
"""
import os
import json
import subprocess

from tempfile import TemporaryFile
from difflib import unified_diff

from collections import defaultdict

from default import Finder
from utils import read_file

class FileStorage(object):
    def __init__(self, file_path):
        self._file_path = file_path
        self._init_data()

    def _init_data(self):
        if os.path.exists(self._file_path):
            return
        os.makedirs(os.path.dirname(self._file_path))

        data = {}
        self._save_data(data)

    def _load_data(self):
        with open(self._file_path, 'r') as fp:
            self._data = json.load(fp)

    def _save_data(self):
        with open(self._file_path, 'w') as fp:
            json.dump(self._data, fp)


class BaseFinder(object):

    """Base class of Finder"""

    def __init__(self, session):
        self._session = session
        pass

    def find(self, file):
        """查询file对应的目的路径

        Args:
            file (file.File): 需要查询的文件对象

        Returns: 成功返回远程的file信息，失败返回None

        """
        pass


class MapFinder(BaseFinder, FileStorage):

    """基于路径映射获取远程路径"""
    def __init__(self, session, map_file=Finder.MAP_DATA_FILE):
        FileStorage.__init__(self, map_file)
        BaseFinder.__init__(self, session)

    def refresh(self):
        self._load_data()

    def add_map(self, file, remote):
        pass

    def find(self, file):
        return self._data.get(self._session.repo, {}).get(file.rpath, None)


class NameFinder(BaseFinder, FileStorage):
    """基于文件名匹配获取匹配度最高的远程路径"""

    def __init__(self, session, cache_file=Finder.NAME_CACHE_FILE):
        BaseFinder.__init__(self, session)
        FileStorage.__init__(self, cache_file)

    def _refresh_cache(self):
        repo_files = []
        for root in self._session.roots:
            root_files = self._session.find_files(root)
            root_abs_files = [os.path.join(root, f) for f in root_files]
            repo_files.append(root_abs_files)

        # dict: filename -> files
        files_dict = defaultdict([])
        for file in repo_files:
            name = os.path.basename(file)
            files_dict[name].append(file)

        self._data[self._repo] = files_dict

    def _find_from_cache(self, file):
        repo_files = self._data.get(file.repo, defaultdict([]))

        return repo_files[file.name]

    def _find_from_remote(self, file):
        self._refresh_cache()

        return self._find_from_cache(file)

    def find(self, file):
        files = self._find_from_cache(file)

        if not files:
            files = self._find_from_remote(file)

        if len(files) == 1:
            return files[0]


class DiffFinder(NameFinder):
    def _get_diff(cls, file1, file2):
        diff_lines = unified_diff(file1, file2)

        return sum(1 for x in diff_lines)

    def _get_file_diff(self, local, remote):
        local_file = local.content

        remote_fp = TemporaryFile()
        self._session.get(remote_file, remote)
        remote_file = remote_fp.readlines()

        diff = self._get_diff(local_file, remote_file)

        return {
                'file': remote,
                'diff': diff
                }

    def _find_min_diff_file(self, file, files):
        file_diffs = []
        for remote_file in files:
            file_diff = self._get_file_diff(file, remote)
            file_diffs.append(file_diff)

        file_diffs.sort('diff')

        # TODO: 100%差异无效
        return file_diffs[0]

    def find(self, file):
        files = self._find_from_remote(file)

        if not files:
            return
        return self._find_min_diff_file(file, files)


class ManualFinder(NameFinder, MapFinder):
    """手动辅助获取远程路径"""

    def _find_remote_files(self):
        self._refresh_cache()

        repo_files = self._data.get(self._session.repo, {})
        remote_files = []
        for files in remote_files.values():
            remote_files.extend(files)

        return remote_files

    def _find_base_files(self, file, files):
        """使用FZF模糊匹配"""
        stdio_fp  = TemporaryFile()
        stdio_fp.writelines(files)
        stdio_fp.seek(0)

        stdout_fp = TemporaryFile()

        fzf_header = '--header="Find remote path for file:%s"' % file.name
        fzf_query = '--query="%s"' % file.name
        fzf_cmd = ['fzf', fzf_header, fzf_query, '--print-query']

        returncode = subprocess.call(fzf_cmd, stdin=stdio_fp, stdout=stdout_fp, shell=True)
        if returncode != 0:
            return
        stdout_fp.seek(0)
        stdout_lines = stdout_fp.readlines()

        return stdout_lines[1]

    def find(self, file):
        files = self._find_remote_files()
        map_file = self._find_base_files(file, files)

        if not map_file:
            return

        self.add_map(file, map_file)
        return map_file
