
import os
import math
from pathlib import Path
import subprocess
import sys
from typing import Iterable, Iterator
import shutil

def file_split(files: Iterable[Path], node_count: int = None, tile_length:int =None, use_lastools=True):
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

files = [f for f in os.listdir('.') if os.path.isfile(f)]
print(files)
file_split(files, node_count = 4, tile_length=None, use_lastools=False)