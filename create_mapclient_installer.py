#!/usr/bin/env python
import argparse
import os
import os.path
import platform
import subprocess
import sys
import time

MAP_CLIENT_REPO = "mapclient"

here = os.path.abspath(os.path.dirname(__file__))


def main():
    parser = argparse.ArgumentParser(prog="installer_preparation")
    parser.add_argument("mapclient_release", help="tag from mapclient codebase")
    parser.add_argument('-v', '--variant', help='variant label for this build')
    parser.add_argument('-l', '--local', help='absolute path to locally available MAP Client')
    args = parser.parse_args()

    local_mapclient = args.local

    variant = args.variant if args.variant is not None else ''
    variant = '' if variant == 'standard' else variant

    current_directory = os.getcwd()
    working_env = os.environ.copy()

    # Define a release name from the release tag
    tag = args.mapclient_release
    tag_parts = tag[1:].split('.')
    release_name = '.'.join(tag_parts[:3])

    result = subprocess.run([sys.executable, "-V"])

    if platform.system() == "Windows":
        os.chdir(os.path.join(local_mapclient, "res", "win"))
        result = subprocess.run([sys.executable, "create_installer.py", release_name, variant], env=working_env)
        print(' == result create installer:', result.returncode, flush=True)
        os.chdir(current_directory)
    elif platform.system() == "Darwin":
        os.chdir(os.path.join(local_mapclient, "res", "macos"))
        result = subprocess.run(["/bin/bash", "create_installer.sh", release_name, f"-{variant}" if variant else ''], env=working_env)
        print(' == result create installer:', result.returncode, flush=True)
        retries = [1, 3, 5]
        retry_index = 0
        while result.returncode:
            time.sleep(retries[retry_index])
            result = subprocess.run(["/bin/bash", "create_installer.sh", release_name, f"-{variant}" if variant else ''], env=working_env)
            print(' == result create installer:', result.returncode, flush=True)

        os.chdir(current_directory)

    if result.returncode:
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
