#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2023 Fabrice Luo <fabriceluo@outlook.com>
#
# Distributed under terms of the MIT license.

"""
缺省值定义位置
"""

import os

PROJECT_NAME='missile'

class Finder(object):
    MAP_DATA_FILE=os.path.expanduser('~/.config/%s/file_map.json' % PROJECT_NAME)
    NAME_CACHE_FILE=os.path.expanduser('~/.config/%s/name_cache.json' % PROJECT_NAME)
