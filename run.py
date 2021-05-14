from argparse import Namespace
import os
import asyncio
import shutil
import csv
import sys

from utils.timer import Timer

from utils.check_requirements import check_requirements


async def init():
    check_requirements()

    # Imports need to be done after the requirements are checked / installed
    from utils.init_argparse import init_argparse
    from utils.utils import get_nodes
    from utils.colorstr import colorstr
    from utils.timer import Timer
    from utils.check_requirements import install_lastools
    from utils.clean_up import clean_up

    # LAStools is required to split pointclouds on devices with lower memory
    install_lastools()

    benchmark_timer = Timer(text=colorstr('yellow', 'bold',
                                          "Benchmark completed in {:0.2f} seconds, results saved to benchmark.csv"))
    benchmark_timer.start()
    parser = init_argparse()

    args = parser.parse_args()

    if args.cloud_compare:
        raise NotImplementedError(
            "Cloud compare functionality not yet implemented")

    if args.benchmark:
        nodes = get_nodes()
        file = open('benchmark.csv', 'w', newline='')
        writer = csv.writer(file)
        writer.writerow(["Node Count", "Remote Files", "Program Time", "Setup Time",
                         "Split Time", "Transfer Time", "Processing Time", "Retrieval Time", "Merge Time"])
        file.flush()
        for i in range(1, len(nodes)+1):
            print(colorstr('yellow', 'bold',
                           f"Starting benchmark loop {i} of {len(nodes)}"))

            timers, file_count = await main(args, main_nodes=nodes[:i])
            writer.writerow([i, file_count, timers["program_timer"], timers["setup_timer"], timers["split_timer"],
                             timers["transfer_timer"], timers["processing_timer"], timers["retrieval_timer"], timers["merge_timer"]])
            file.flush()
        file.close()
        benchmark_timer.stop()

    else:
        await main(args)


async def main(args: Namespace, main_nodes=None):

    from utils.file_utils import file_split, process_files, merge, check_output_dir
    from utils.utils import get_nodes, transfer_files
    from utils.colorstr import colorstr
    from utils.clean_up import clean_up, async_clean_up
    import atexit

    timers = {}

    program_timer = Timer(text=colorstr(
        'blue', 'bold', "Done! Program completed in {:0.2f} seconds"))
    program_timer.start()
    print("Starting program timer\n")

    files = process_files(args.files)

    if main_nodes is None:
        nodes = get_nodes()
    else:
        nodes = main_nodes

    if args.benchmark:
        overwrite_output = True
    else:
        args.output, overwrite_output = check_output_dir(args.output)

    setup_nodes = []

    setup_timer = Timer(
        text=colorstr('blue', "Setup of nodes completed in {:.2f} seconds"))
    setup_timer.start()
    results = await asyncio.gather(*[node.setup() for node in nodes])
    timers["setup_timer"] = setup_timer.stop()

    for i in range(len(results)):
        if results[i]:
            setup_nodes.append(nodes[i])

    print("----------------------------------")
    if len(setup_nodes) == 0:
        print(
            colorstr('red', 'bold', '\nNo nodes where set up correctly, exiting\n'))
    else:
        if len(setup_nodes) != len(nodes):
            if (args.benchmark):
                print(colorstr(
                    'red', 'bold', 'Cannot benchmark without all available nodes, please check your node setup'))
                sys.exit(1)
            print(
                f"Not all nodes set up correctly,\ncontinuing with {len(setup_nodes)} node(s): {[node.host for node in setup_nodes]}\n")

        print('Splitting files locally...')
        split_timer = Timer(text=colorstr(
            'blue', "File(s) split in {:0.2f} seconds"))
        split_timer.start()
        paths = file_split(files, node_count=len(
            setup_nodes), tile_length=args.tile_length)
        timers["split_timer"] = split_timer.stop()

        # Now that the splits have been completed, we want to register a cleanup function in case the function fails
        atexit.register(clean_up, paths, nodes)

        print('Copying files to remote nodes...')
        transfer_timer = Timer(
            text=colorstr('blue', "Copying from local to nodes completed in {:.2f} seconds"))
        transfer_timer.start()
        await transfer_files(files, args.pipeline, setup_nodes)
        timers["transfer_timer"] = transfer_timer.stop()

        pipeline = args.pipeline.split('/')[-1]

        print("\nStarting remote execution...")
        processing_timer = Timer(text=colorstr(
            'blue', "All remote processing completed in {:0.2f} seconds"))
        processing_timer.start()
        await asyncio.gather(*[node.remote_exec(pipeline) for node in setup_nodes])
        timers["processing_timer"] = processing_timer.stop()

        print("\nRetrieving remote files...")
        if overwrite_output:
            shutil.rmtree(args.output)

        # If the directory already exists, os.mkdir will silently fail
        os.mkdir(args.output)

        retrieval_timer = Timer(
            text=colorstr('blue', "Copying from nodes to local completed in {:.2f} seconds"))
        retrieval_timer.start()
        await asyncio.gather(*[node.get(args.output) for node in setup_nodes])
        timers["retrieval_timer"] = retrieval_timer.stop()

        print("Merging...")
        merge_timer = Timer(text=colorstr(
            'blue', "File(s) merged in {:0.2f} seconds"))
        merge_timer.start()
        merge(args.output, files)
        timers["merge_timer"] = merge_timer.stop()

        timers["program_timer"] = program_timer.stop()

        # Cleanup in between runs instead of just at exit
        if args.benchmark:
            await async_clean_up(paths, nodes)
        
        return (timers, len(paths))

if __name__ == '__main__':
    try:
        asyncio.run(init())
    except KeyboardInterrupt:
        print('Cancelling')
        sys.exit(1)
