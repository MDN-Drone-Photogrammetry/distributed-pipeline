
import os
from pathlib import Path
import subprocess
import sys
from typing import Iterator


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


def file_split(files, len_nodes):
    paths = []
    for file in files:
        result = subprocess.check_output(["pdal", "info", file, "--stats"])
        start = str(result).find('count')
        if start == -1:
            print('Count not found in {file}')
        else:
            end = str(result).find(',', start)
            size = str(result)[start+8:end]

        split_size = int(int(size)/len_nodes)
        print(
            f"{file} has {size} points, Splitting into {len_nodes} files of {split_size} points")
        split_path = Path.joinpath(file.parents[0], 'split')
        if not split_path.exists():
            os.mkdir(split_path)
        path = Path.joinpath(split_path, file.name)
        paths.append(path)
        result = subprocess.run(
            ["pdal", "split", "--capacity", str(split_size), file, path])
        print("")

    return paths
