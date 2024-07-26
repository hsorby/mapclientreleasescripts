#!/usr/bin/env python
import argparse
import glob
import os
import os.path
import shutil
import subprocess
import sys


MAP_CLIENT_REPO = "mapclient"

here = os.path.abspath(os.path.dirname(__file__))


def main():
    parser = argparse.ArgumentParser(prog="application_preparation")
    parser.add_argument("mapclient_release", help="tag from mapclient codebase")
    parser.add_argument('-v', '--variant', help='variant label for this build')
    parser.add_argument('-l', '--local', help='absolute path to locally available MAP Client')
    parser.add_argument("--pre", action='store_true', help="Allow pre-release versions")
    args = parser.parse_args()

    cut_short = False
    local_mapclient = args.local

    variant = args.variant if args.variant is not None else ''
    variant = '' if variant == 'standard' else variant

    available_pips = glob.glob(os.path.join(os.path.dirname(sys.executable), 'pip*'))
    if len(available_pips) == 0:
        sys.exit(1)

    pip = available_pips[0]

    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    print(' == result install:', result.returncode, flush=True)

    # Always install numpy, and scipy
    result = subprocess.run([pip, "install", "numpy!=2.0.1,!=2.0.0", "scipy"])
    print(' == result install extras:', result.returncode, flush=True)

    if local_mapclient is None:
        mapclient_url = f"https://github.com/MusculoskeletalAtlasProject/{MAP_CLIENT_REPO}"
        local_mapclient = MAP_CLIENT_REPO
        result = subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", mapclient_url, "-b", args.mapclient_release])
        print(' == result git:', result.returncode, flush=True)

    result = subprocess.run([pip, "install", "-e", f"{local_mapclient}/src"])
    print(' == result install:', result.returncode, flush=True)

    plugins_file = os.path.join(here, "plugin_listing.txt")
    have_plugins = os.path.isfile(plugins_file)
    if have_plugins:
        prepare_plugin_cmd = [sys.executable, os.path.join(here, "prepare_mapclient_plugins.py"), plugins_file]
        if args.pre:
            prepare_plugin_cmd.append("--pre")
        result = subprocess.run(prepare_plugin_cmd)
        print(' == result plugins preparation:', result.returncode, flush=True)

    working_env = os.environ.copy()

    workflows_file = os.path.join(here, "workflow_listing.txt")
    if os.path.isfile(workflows_file):
        result = subprocess.run([sys.executable, os.path.join(here, "prepare_mapclient_workflows.py"), workflows_file])
        print(' == result workflow preparation:', result.returncode, flush=True)

        working_env["INTERNAL_WORKFLOWS_ZIP"] = os.path.abspath('internal_workflows.zip')

    if cut_short:
        return

    current_directory = os.getcwd()
    os.chdir(os.path.join(local_mapclient, "res", "pyinstaller"))

    # Dirty hack for fixing namespace package finding.
    if have_plugins:
        shutil.move(os.path.join(current_directory, 'mapclientplugins_paths.txt'), os.path.join(os.getcwd(), 'mapclientplugins_paths.txt'))

    result = subprocess.run([sys.executable, "create_application.py", variant], env=working_env)
    print(' == result application creation:', result.returncode, flush=True)
    os.chdir(current_directory)

    if result.returncode:
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
