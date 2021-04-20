
import subprocess
import asyncio
from utils.timer import Timer
from utils.file_utils import file_split, process_files

from utils.init_argparse import init_argparse
from utils.utils import check_requirements, colorstr, get_nodes, transfer_files

async def main():
    program_timer = Timer(text="Done! Program completed in {:0.2f} seconds")
    program_timer.start()

    check_requirements()

    # Imports need to be done after the requirements are checked / installed
    from utils.file_utils import file_split, process_files
    from utils.init_argparse import init_argparse
    from utils.utils import get_nodes, transfer_files

    parser = init_argparse()

    args = parser.parse_args()

    files = process_files(args.files)

    nodes = get_nodes()

    setup_nodes = []
    for node in nodes:
        success = await node.setup()

        if success:
            setup_nodes.append(node)

    print("----------------------------------")
    if len(setup_nodes) == 0:
        print(
            f"\n{colorstr('red', 'bold', 'No nodes where set up correctly, exiting')}\n")

    else:
        if len(setup_nodes) != len(nodes):
            print(
                f"Not all nodes set up correctly,\ncontinuing with {len(setup_nodes)} node(s): {[node.host for node in setup_nodes]}\n")

        paths = file_split(files, len(setup_nodes))
        transfer_files(files, setup_nodes)

        print("\nStarting remote execution...")
        processing_timer = Timer(text="All remote processing completed in {:0.2f} seconds")
        processing_timer.start()

        # await nodes[1].remote_exec()
        # tasks = []
        # for node in setup_nodes:
        #     task = asyncio.create_task(node.remote_exec())
        #     tasks.append(task)
        #     # await node.remote_exec()
        # print('test')
        # await asyncio.gather(*tasks)
        await asyncio.wait([node.remote_exec() for node in nodes])
        # await asyncio.gather(*[node.remote_exec() for node in nodes])
        processing_timer.stop()

        print("")

        print("Cleaning up...")
        for path in paths:
            subprocess.run(["rm", "-r", path.parents[0]])

        program_timer.stop()


if __name__ == '__main__':
    asyncio.run(main())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())