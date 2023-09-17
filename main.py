#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Fabrice Luo <fabriceluo@outlook.com>
#
# Distributed under terms of the MIT license.

"""
Code Sync.
"""
import os
import logging

import click
from watchdog.observers import Observer

from session import Session
from watcher import CodeEventHandler
from finder import (MapFinder, NameFinder, DiffFinder, ManualFinder)
from utils import (
    get_git_repo,
    get_git_root,
    get_remote_roots,
)


@click.group()
def main():
    pass


@main.command()
@click.option('--host')
@click.option('--port')
@click.option('--username')
@click.option('--password')
@click.option('--workdir')
def watch(host, port, username, password, workdir):
    host = host or os.environ['REMOTE_HOST']
    port = port or os.environ['REMOTE_PORT']
    username = username or os.environ['REMOTE_USERNAME']
    password = password or os.environ['REMOTE_USERNAME']

    assert (host)
    assert (port)
    assert (username)
    assert (password)

    repo_root = get_git_root(workdir)
    repo_name = get_git_repo(workdir)
    roots = get_remote_roots(repo_name)

    session = Session(roots, host, port, username, password)

    finders = [
        MapFinder(session),
        NameFinder(session),
        DiffFinder(session),
    ]
    handler = CodeEventHandler(repo_root, repo_name, session, finders)

    observer.schedule(handler, repo_root, recursive=True)
    observer.start()
    try:
        while observer.isAlive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


def manual_map():
    pass


if __name__ == "__main__":
    main()
