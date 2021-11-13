#!/usr/bin/env python
import argparse
import os.path
import re
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(prog="workflow_preparation")
    parser.add_argument("workflow_listing", help="A file of workflows to prepare")
    args = parser.parse_args()

    if not os.path.exists(args.workflow_listing):
        sys.exit(1)

    with open(args.workflow_listing) as f:
        workflows = f.readlines()

    current_dir = os.getcwd()
    if not os.path.exists('workflows'):
        os.mkdir('workflows')

    os.chdir('workflows')
    default_workflow_set = False
    for workflow_info in workflows:
        parts = workflow_info.split()
        if len(parts) == 2:
            url = parts[0]
            tag = parts[1]
            if not default_workflow_set:
                default_workflow_set = True
                with open('default_workflow.txt', 'w') as f:
                    f.write(os.path.basename(url))

            result = subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--depth", "1", url, "-b", tag])
            print(' == result git:', result.returncode, flush=True)
            try:
                result.check_returncode()
            except subprocess.CalledProcessError as e:
                if e.returncode == 128:
                    print(' == skipping existing expecting version:', tag[1:], flush=True)
                else:
                    sys.exit(e.returncode)

    os.chdir(current_dir)
    if len(workflows):
        shutil.make_archive('internal_workflows', 'zip', './workflows')


if __name__ == "__main__":
    main()
