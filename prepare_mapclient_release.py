#!/usr/bin/env python
import argparse
import glob
import os
import os.path
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(prog="release_preparation")
    parser.add_argument("mapclient_release", help="tag from mapclient codebase")
    parser.add_argument('-p', '--plugins', help='input plugins list file')
    parser.add_argument('-w', '--workflows', help='input workflows list file')
    parser.add_argument('-v', '--variant', help='variant label for this build')
    args = parser.parse_args()

    variant = args.variant if args.variant is not None else ''

    available_pips = glob.glob(os.path.join(os.path.dirname(sys.executable), 'pip*'))
    if len(available_pips) == 0:
        sys.exit(1)

    pip = available_pips[0]

    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    print(' == result install:', result.returncode, flush=True)

    # Always install opencmiss.zinc, numpy, and scipy
    result = subprocess.run([pip, "install", "opencmiss.zinc", "numpy", "scipy"])
    print(' == result install extras:', result.returncode, flush=True)

    mapclient_url = "https://github.com/MusculoskeletalAtlasProject/mapclient"
    result = subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", mapclient_url, "-b", args.mapclient_release])
    print(' == result git:', result.returncode, flush=True)

    result = subprocess.run([pip, "install", "-e", 'mapclient/src'])
    print(' == result install:', result.returncode, flush=True)

    if args.plugins is not None and os.path.isfile(args.plugins):
        result = subprocess.run([sys.executable, "prepare_mapclient_plugins.py", args.plugins])
        print(' == result plugins preparation:', result.returncode, flush=True)

    working_env = os.environ.copy()

    if args.workflows is not None and os.path.isfile(args.workflows):
        result = subprocess.run([sys.executable, "prepare_mapclient_workflows.py", args.workflows])
        print(' == result workflow preparation:', result.returncode, flush=True)

        working_env["INTERNAL_WORKFLOWS_ZIP"] = os.path.abspath('internal_workflows.zip')

    current_directory = os.getcwd()
    os.chdir("mapclient/res/pyinstaller/")
    result = subprocess.run([sys.executable, "create_application.py", variant], env=working_env)
    print(' == result application creation:', result.returncode, flush=True)
    os.chdir(current_directory)

    if platform.system() == "Windows":
        os.chdir("mapclient/res/win")
        result = subprocess.run([sys.executable, "create_installer.py", args.mapclient_release, variant], env=working_env)
        print(' == result create installer:', result.returncode, flush=True)
        os.chdir(current_directory)
    elif platform.system() == "Darwin":
        os.chdir("mapclient/res/macos")
        result = subprocess.run(["/bin/bash", "create_installer.sh", args.mapclient_release, f"-{variant}" if variant else ''], env=working_env)
        print(' == result create installer:', result.returncode, flush=True)
        os.chdir(current_directory)


if __name__ == "__main__":
    main()
