#!/usr/bin/env python
import argparse
import os
import os.path
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(prog="release_preparation")
    parser.add_argument("mapclient_release", help="A tag from mapclient codebase")
    parser.add_argument("plugin_listing", help="A file of plugins to prepare")
    parser.add_argument("workflow_listing", help="A file of workflows to prepare")
    args = parser.parse_args()

    if not os.path.exists(args.plugin_listing):
        sys.exit(1)

    if not os.path.exists(args.workflow_listing):
        sys.exit(2)

    mapclient_url = "https://github.com/MusculoskeletalAtlasProject/mapclient"
    result = subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", mapclient_url, "-b", args.mapclient_release])
    print(' == result git:', result.returncode)

    result = subprocess.run(["pip", "install", "-e", 'mapclient/src'])
    print(' == result install:', result.returncode)

    result = subprocess.run([sys.executable, "prepare_mapclient_plugins.py", args.plugin_listing])
    print(' == result plugins preparation:', result.returncode)

    result = subprocess.run([sys.executable, "prepare_mapclient_workflows.py", args.workflow_listing])
    print(' == result workflow preparation:', result.returncode)

    working_env = os.environ.copy()
    working_env["INTERNAL_WORKFLOWS_ZIP"] = os.path.abspath('internal_workflows.zip')

    current_directory = os.getcwd()
    os.chdir("mapclient/res/pyinstaller/")
    result = subprocess.run([sys.executable, "create_application.py"], env=working_env)
    print(' == result application creation:', result.returncode)
    os.chdir(current_directory)


if __name__ == "__main__":
    main()
