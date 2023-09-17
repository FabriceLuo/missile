#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Fabrice Luo <fabriceluo@outlook.com>
#
# Distributed under terms of the MIT license.

"""
工具函数
"""

import git

def read_file(file):
    with open(file) as fp:
        return fp.read()

def get_git_root(path):
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    return git_root

def get_git_repo(path):
    git_repo = git.Repo(path, search_parent_directories=True)
    repo_name = git_repo.remotes.origin.url.split('.git')[0].split('/')[-1]

    return repo_name

def get_remote_roots(repo):
    pass
