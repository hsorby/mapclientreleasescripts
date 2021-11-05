#!/usr/bin/env python
import argparse
import os.path
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(prog="plugin_preparation")
    parser.add_argument("plugin_listing", help="A file of plugins to prepare")
    args = parser.parse_args()

    if not os.path.exists(args.plugin_listing):
        sys.exit(1)

    with open(args.plugin_listing) as f:
        plugins = f.readlines()

    for plugin_info in plugins:
        parts = plugin_info.split()
        if len(parts) == 2:
            url = parts[0]
            tag = parts[1]
            result = subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", url, "-b", tag])
            print(' == result git:', result.returncode)
            try:
                result.check_returncode()
            except subprocess.CalledProcessError as e:
                if e.returncode == 128:
                    print(' == skipping existing expecting version:', tag[1:])
                else:
                    sys.exit(e.returncode)

            dir_name = os.path.basename(url)
            if dir_name.endswith(".git"):
                dir_name = re.sub(".git$", "", dir_name)

            result = subprocess.run(["pip", "install", "-e", dir_name])
            print(' == result install:', result.returncode)
            result.check_returncode()


if __name__ == "__main__":
    main()
