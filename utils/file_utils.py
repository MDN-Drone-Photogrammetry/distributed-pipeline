
import os
import math
from pathlib import Path
import subprocess
import sys
from typing import Iterable, Iterator
import shutil

# approved_types = ['ply', 'laz', 'las'], # Not sure if this is required


def process_files(args_files) -> Iterator[Path]:
    if len(args_files) == 0:
        print("No files provided, exiting...")
        sys.exit()

    files = []
    for file in args_files:
        path = Path(file)
        if path.is_file():
            files.append(path)
        else:
            print(f"{file} is not a file or directory, skipping")

    if len(files) == 0:
        print(f"No files found in {args_files}, exiting...")
        sys.exit()
    else:
        print(f"{len(files)} file(s) found, {[str(file) for file in files]}\n")

    return files


def file_split(files: Iterable[Path], node_count=None, tile_length=None, use_lastools=True):
    paths = []

    for file in files:
        if node_count == 1:
            output_dir = Path.joinpath(file.parents[0], 'split')
            if not os.path.isdir(output_dir):
                os.mkdir(output_dir)
            split_path = Path.joinpath(output_dir, file.name)
            shutil.copyfile(file, split_path)
            paths.append(split_path)
            continue

        result = subprocess.check_output(["pdal", "info", file, "--stats"])
        start = str(result).find('count')
        if start == -1:
            print('Count not found in {file}')
        else:
            end = str(result).find(',', start)
            size = str(result)[start+8:end]

        split_size = int(math.ceil(int(size)/node_count))
        if tile_length is None:
            print(
                f"{file} has {size} points, splitting into {node_count} files of {split_size} points")
        else:
            print(f"{file} has {size} points")
        split_path = Path.joinpath(file.parents[0], 'split')
        if not split_path.exists():
            os.mkdir(split_path)
        
        if use_lastools:
            nstring = len(str(node_count))
            filename = f'{file.name.split(".")[0]}_{0*nstring}'
        else:
            filename = file.name

        path = Path.joinpath(split_path, filename)
        paths.append(path)

        if tile_length is None:
            if use_lastools:
                output = subprocess.run(
                    ["./LAStools/bin/lasmerge", "-i", file, "-o", path, "-split", str(split_size)])
            else:
                output = subprocess.run(
                    ["pdal", "split", "--capacity", str(split_size), file, path])

        else:
            output = subprocess.run(
                ["pdal", "split", "--length", str(tile_length), file, path])

        if output.stderr is not None:
            print(output.stderr)
        print("")

    return paths


def check_output_dir(output):
    overwrite_output = False
    new_dir = None

    while os.path.isdir(output):
        response = None
        while response == None:
            response = input(
                f"{output} already exists, would you like to overwrite? [Y/n]: ").lower().strip()
            if response == '' or response == 'y':
                overwrite_output = True
                break
            else:
                new_dir = input(f"Please choose another output dir: ")
                output = new_dir
        if overwrite_output:
            break

    if new_dir is not None:
        os.mkdir(new_dir)

    return output, overwrite_output


def merge(output, files: Iterator[Path]):

    output_files = [f for f in os.listdir(
        output) if os.path.isfile(os.path.join(output, f))]

    for file in files:
        files_to_merge = []
        for output_file in output_files:
            name = file.name.split('.')[0]
            if name in output_file:
                files_to_merge.append(os.path.join(output, output_file))

        output_path = os.path.join(output, file.name)
        if len(output_files) == 1:
            shutil.copyfile(output_files[0], output_path)

        else:
            subprocess.run(
                ["pdal", "merge", *files_to_merge, output_path])
        for file_to_remove in files_to_merge:
            os.remove(file_to_remove)

def cleanup(paths):
    print("Cleaning up...")
    if len(paths) > 0:
        for path in paths:
            subprocess.run(["rm", "-r", path.parents[0]])
