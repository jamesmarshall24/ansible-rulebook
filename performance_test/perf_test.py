#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Usage:
    perf_test [options] <cmd> <name> <type> <n>

Options:
    -h, --help        Show this page
    --debug            Show debug logging
    --verbose        Show verbose logging
    --no-header
    --only-header
"""
import csv
import logging
import subprocess
import sys
import time

from docopt import docopt

logger = logging.getLogger(__name__)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = docopt(__doc__, args)
    if parsed_args["--debug"]:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args["--verbose"]:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    writer = csv.DictWriter(
        sys.stdout, fieldnames=["cmd", "name", "type", "n", "time"]
    )
    if not parsed_args["--no-header"]:
        writer.writeheader()
    if parsed_args["--only-header"]:
        return
    start = time.time()
    try:
        subprocess.check_output(parsed_args["<cmd>"], shell=True)
    except BaseException:
        print(parsed_args["<cmd>"])
        raise
    end = time.time()
    writer.writerow(
        dict(
            cmd=parsed_args["<cmd>"],
            name=parsed_args["<name>"],
            type=parsed_args["<type>"],
            n=parsed_args["<n>"],
            time=end - start,
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
