#!/usr/bin/env python
import argparse
import glob
import json
import os.path
import re
import subprocess
import sys

def _parse_args():
    parser = argparse.ArgumentParser(prog="plugin_preparation")
    parser.add_argument("plugin_listing", help="A file of plugins to prepare")
    parser.add_argument("-p", "--pre", action='store_true', help="Allow pre-release versions")
    parser.add_argument('-r', '--repos', default='.', help='path to where repositories should be cloned')
    return parser.parse_args()


def main():
    args = _parse_args()

    if not os.path.exists(args.plugin_listing):
        sys.exit(2)

    available_pips = glob.glob(os.path.join(os.path.dirname(sys.executable), 'pip*'))
    if len(available_pips) == 0:
        sys.exit(3)

    pip = available_pips[0]

    with open(args.plugin_listing) as f:
        plugins = f.readlines()

    current_dir = os.getcwd()
    repos_dir = os.path.abspath(args.repos)
    plugin_paths = {}
    for plugin_info in plugins:
        parts = plugin_info.split()
        if len(parts) > 0:
            url = parts[0]

            dir_name = os.path.basename(url)
            if dir_name.endswith(".git"):
                dir_name = re.sub(".git$", "", dir_name)

            cloned_dir = os.path.join(repos_dir, dir_name)
            clone_command = ["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", url, cloned_dir]
            tag = None
            if len(parts) > 1:
                tag = parts[1]
                clone_command.extend(["-b", tag])

            if not args.pre and tag is None:
                raise AssertionError(f"Pre-release is not specified and plugin '{url}' has no tag set.")

            result = subprocess.run(clone_command)
            print(' == result git:', result.returncode, flush=True)
            try:
                result.check_returncode()
            except subprocess.CalledProcessError as e:
                if e.returncode == 128:
                    print(' == skipping existing expecting version:', tag[1:] if tag is not None else "default")
                else:
                    sys.exit(e.returncode)

            requirements_file = os.path.join(os.path.abspath(cloned_dir), 'requirements.txt')
            if os.path.isfile(requirements_file) and os.stat(requirements_file).st_size > 0:
                plugin_paths[cloned_dir] = 'requirements_file'
                pip_install_cmd = [pip, 'install', '-r', requirements_file]
            else:
                plugin_paths[cloned_dir] = 'installed'
                pip_install_cmd = [pip, 'install', '-e', cloned_dir]

            if args.pre is not None:
                pip_install_cmd.append('--pre')

            result = subprocess.run(pip_install_cmd)
            print(' == result install:', result.returncode, flush=True)
            result.check_returncode()

    plugin_paths_file = os.path.join(current_dir, 'mapclientplugins_paths.json')
    with open(plugin_paths_file, 'w') as fh:
        json.dump(plugin_paths, fh)

    print(' == mapclientplugins path file:')

    with open(plugin_paths_file) as fh:
        print(fh.read())


if __name__ == "__main__":
    main()
