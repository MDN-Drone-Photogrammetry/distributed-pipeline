
import subprocess
import sys

from utils.check_requirements import check_requirements


if __name__ == '__main__':
    check_requirements()

    # Imports need to be done after the requirements are checked / installed
    from utils.file_utils import file_split, process_files
    from utils.init_argparse import init_argparse
    from utils.utils import get_nodes, transfer_files

    parser = init_argparse()

    args = parser.parse_args()

    files = process_files(args.files)

    nodes = get_nodes()

    if (len(nodes)) == 0:
        print("\nNo available remote nodes to run on, exiting...\n")
        sys.exit()

    paths = file_split(files, len(nodes))

    transfer_files(files, nodes)

    for node in nodes:
        node.remote_exec()
    
    print("")

    print("Cleaning up...")
    for path in paths:
        subprocess.run(["rm", "-r", path.parents[0]])
    print("Done!")