
import os
from pathlib import Path
import subprocess
from utils.file_utils import file_split, process_files

from utils.init_argparse import init_argparse
from utils.utils import check_requirements, get_nodes, transfer_files


if __name__ == '__main__':
    check_requirements()

    parser = init_argparse()

    args = parser.parse_args()

    files = process_files(args.files)

    nodes = get_nodes()

    paths = file_split(files, len(nodes))

    transfer_files(files, nodes)

    for node in nodes:
        node.remote_exec()
    
    print("")

    print("Cleaning up...")
    for path in paths:
        subprocess.run(["rm", "-r", path.parents[0]])
    print("Done!")