import os
import subprocess
import asyncio
import shutil
from utils.file_utils import check_output_dir, merge

from utils.timer import Timer

from utils.check_requirements import check_requirements

async def main():
    check_requirements()

    # Imports need to be done after the requirements are checked / installed
    from utils.file_utils import file_split, process_files
    from utils.init_argparse import init_argparse
    from utils.utils import get_nodes, transfer_files
    from utils.colorstr import colorstr

    program_timer = Timer(text=colorstr('blue', "Done! Program completed in {:0.2f} seconds"))
    program_timer.start()
    print("Starting program timer\n")

    parser = init_argparse()

    args = parser.parse_args()

    files = process_files(args.files)

    nodes = get_nodes()

    args.output, overwrite_output = check_output_dir(args.output)
    
    setup_nodes = []

    network_timer = Timer()
    results = await asyncio.gather(*[node.setup() for node in nodes])

    for i in range(len(results)):
        if results[i]:
            setup_nodes.append(nodes[i])

    print("----------------------------------")
    if len(setup_nodes) == 0:
        print(
            f"\n{colorstr('red', 'bold', 'No nodes where set up correctly, exiting')}\n")

    else:
        if len(setup_nodes) != len(nodes):
            print(
                f"Not all nodes set up correctly,\ncontinuing with {len(setup_nodes)} node(s): {[node.host for node in setup_nodes]}\n")

        paths = file_split(files, node_count=len(setup_nodes), tile_length=args.tile_length)
        await transfer_files(files, setup_nodes)

        print("\nStarting remote execution...")
        processing_timer = Timer(text=colorstr('blue', "All remote processing completed in {:0.2f} seconds"))
        processing_timer.start()

        await asyncio.gather(*[node.remote_exec() for node in setup_nodes])
        processing_timer.stop()

        print("\nRetrieving remote files")
        if overwrite_output:
            shutil.rmtree(args.output)
        os.mkdir('./output')
        await asyncio.gather(*[node.get(args.output) for node in setup_nodes])

        print("Merging...")
        merge(args.output, files)

        print("Cleaning up...")
        for path in paths:
            subprocess.run(["rm", "-r", path.parents[0]])

        program_timer.stop()


if __name__ == '__main__':
    asyncio.run(main())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())