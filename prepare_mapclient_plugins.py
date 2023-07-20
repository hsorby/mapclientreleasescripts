#!/usr/bin/env python
import argparse
import glob
import os.path
import re
import site
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(prog="plugin_preparation")
    parser.add_argument("plugin_listing", help="A file of plugins to prepare")
    parser.add_argument("-p", "--pre", action='store_true', help="Allow pre-release versions")
    args = parser.parse_args()

    if not os.path.exists(args.plugin_listing):
        sys.exit(2)

    available_pips = glob.glob(os.path.join(os.path.dirname(sys.executable), 'pip*'))
    if len(available_pips) == 0:
        sys.exit(3)

    pip = available_pips[0]

    with open(args.plugin_listing) as f:
        plugins = f.readlines()

    site_packages_dir = site.getsitepackages()
    print(site_packages_dir)
    sys.exit(3)
    print(' == site packages dir:', site_packages_dir)
    plugin_paths = []
    for plugin_info in plugins:
        parts = plugin_info.split()
        if len(parts) > 0:
            url = parts[0]
            clone_command = ["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", url]
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

            dir_name = os.path.basename(url)
            if dir_name.endswith(".git"):
                dir_name = re.sub(".git$", "", dir_name)

            plugin_paths.append(os.path.abspath(dir_name))
            pip_install_cmd = [pip, "install", "-e", dir_name]
            if args.pre is not None:
                pip_install_cmd.append("--pre")

            result = subprocess.run(pip_install_cmd)
            print(' == result install:', result.returncode, flush=True)
            result.check_returncode()

    with open(os.path.join(site_packages_dir, 'mapclientplugins_paths.pth'), 'w') as f:
        f.writelines(plugin_paths)

    print(' == plugin paths:')
    print(plugin_paths)


if __name__ == "__main__":
    main()
