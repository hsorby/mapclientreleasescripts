#!/usr/bin/env python
import argparse
import glob
import os
import os.path
import platform
import subprocess
import sys


MAP_CLIENT_REPO = "mapclient"

here = os.path.abspath(os.path.dirname(__file__))


def main():
    parser = argparse.ArgumentParser(prog="release_preparation")
    parser.add_argument("mapclient_release", help="tag from mapclient codebase")
    parser.add_argument('-p', '--plugins', help='input plugins list file')
    parser.add_argument('-w', '--workflows', help='input workflows list file')
    parser.add_argument('-v', '--variant', help='variant label for this build')
    parser.add_argument('-l', '--local', help='absolute path to locally available MAP Client')
    parser.add_argument("--pre", action='store_true', help="Allow pre-release versions")
    args = parser.parse_args()

    cut_short = False
    local_mapclient = args.local

    variant = args.variant if args.variant is not None else ''

    available_pips = glob.glob(os.path.join(os.path.dirname(sys.executable), 'pip*'))
    if len(available_pips) == 0:
        sys.exit(1)

    pip = available_pips[0]

    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    print(' == result install:', result.returncode, flush=True)

    # Always install numpy, and scipy
    result = subprocess.run([pip, "install", "numpy", "scipy"])
    print(' == result install extras:', result.returncode, flush=True)

    if local_mapclient is None:
        mapclient_url = f"https://github.com/MusculoskeletalAtlasProject/{MAP_CLIENT_REPO}"
        local_mapclient = MAP_CLIENT_REPO
        result = subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", mapclient_url, "-b", args.mapclient_release])
        print(' == result git:', result.returncode, flush=True)

    result = subprocess.run([pip, "install", "-e", f"{local_mapclient}/src"])
    print(' == result install:', result.returncode, flush=True)

    have_plugins = False
    if args.plugins is not None and os.path.isfile(args.plugins):
        have_plugins = True
        prepare_plugin_cmd = [sys.executable, os.path.join(here, "prepare_mapclient_plugins.py"), args.plugins]
        if args.pre:
            prepare_plugin_cmd.append("--pre")
        result = subprocess.run(prepare_plugin_cmd)
        print(' == result plugins preparation:', result.returncode, flush=True)

    working_env = os.environ.copy()

    if args.workflows is not None and os.path.isfile(args.workflows):
        result = subprocess.run([sys.executable, os.path.join(here, "prepare_mapclient_workflows.py"), args.workflows])
        print(' == result workflow preparation:', result.returncode, flush=True)

        working_env["INTERNAL_WORKFLOWS_ZIP"] = os.path.abspath('internal_workflows.zip')

    if cut_short:
        return

    current_directory = os.getcwd()
    os.chdir(f"{MAP_CLIENT_REPO}/res/pyinstaller/")

    # Dirty hack for fixing namespace package finding.
    if have_plugins:
        os.rename(os.path.join(current_directory, 'mapclientplugins_paths.txt'), os.path.join(os.getcwd(), 'mapclientplugins_paths.txt'))

    result = subprocess.run([sys.executable, "create_application.py", variant], env=working_env)
    print(' == result application creation:', result.returncode, flush=True)
    os.chdir(current_directory)
    if result.returncode:
        sys.exit(result.returncode)

    # Define a release name from the release tag
    tag = args.mapclient_release
    tag_parts = tag[1:].split('.')
    release_name = '.'.join(tag_parts[:3])

    if platform.system() == "Windows":
        os.chdir(f"{MAP_CLIENT_REPO}/res/win")
        result = subprocess.run([sys.executable, "create_installer.py", release_name, variant], env=working_env)
        print(' == result create installer:', result.returncode, flush=True)
        os.chdir(current_directory)
    elif platform.system() == "Darwin":
        os.chdir(f"{MAP_CLIENT_REPO}/res/macos")
        result = subprocess.run(["/bin/bash", "create_installer.sh", release_name, f"-{variant}" if variant else ''], env=working_env)
        print(' == result create installer:', result.returncode, flush=True)
        os.chdir(current_directory)

    if result.returncode:
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
