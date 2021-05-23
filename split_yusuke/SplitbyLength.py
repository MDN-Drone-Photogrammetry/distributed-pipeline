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

        result = subprocess.check_output(["pdal", "info", file])
        #split by counts 
        start = str(result).find('count')
        if start == -1:
            print('Count not found in {file}')
        else:
            end = str(result).find(',', start)
            size = str(result)[start+8:end]
            split_size = int(math.ceil(int(size)/node_count))

        #split by length 
        #find minx
        start = str(result).rfind('minx')
        if start == -1:
            print('Count not found minx in {file}')
        else:
            end = str(result).find(',', start)
            minx = str(result)[start+6:end]

            #find maxx
            start = str(result).rfind('maxx')
            if start == -1:
                print('Count not found maxx in {file}')
            else:
                end = str(result).find(',', start)
                maxx = str(result)[start+6:end]

            #find miny
            start = str(result).rfind('miny')
            if start == -1:
                print('Count not found miny in {file}')
            else:
                end = str(result).find(',', start)
                miny = str(result)[start+6:end]
                
            #find maxy
            start = str(result).rfind('maxy')
            if start == -1:
                print('Count not found maxy in {file}')
            else:
                end = str(result).find(',', start)
                maxy = str(result)[start+6:end]

            print(f"minx is {float(minx)}")
            print(f"maxx is {float(maxx)}")
            print(f"miny is {float(miny)}")
            print(f"maxy is {float(maxy)}")
                
            lengthX = float(maxx) - float(minx)
            lengthY = float(maxy) - float(miny)
            lengthMax = 0
            # check which axis of the point cloud has the longest length
            if lengthX > lengthY :
                lengthMax = lengthX
            else:
                lengthMax = lengthY
            
            # length of the square tile of splited point cloud
            split_length = lengthMax / node_count
            # define buffer
            buffer = split_length*(1/10)
            print(f"length of splited point cloud is {float(lengthMax)}")
            print(f"buffer is {float(buffer)}")
            

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
                print(
                f"{file} has {size} points, splitting into {node_count} files of {split_size} points")
                output = subprocess.run(
                    ["./LAStools/bin/lasmerge", "-i", file, "-o", path, "-split", str(split_size)])
            else:
                #run PDAL split
                print(
                f"deviding {file} of {lengthMax} length, splitting into {node_count} files of square tiles of {split_length} length")
                output = subprocess.run(
                    ["pdal", "split", "--length", str(split_length), "--origin_x", str(minx), "--origin_y",str(miny), "-i", file, "-o", path])

        else:
            output = subprocess.run(
                ["pdal", "split", "--length", str(tile_length), "-i", file, "-o", path])

        if output.stderr is not None:
            print(output.stderr)
        print("")

    return paths

files = [f for f in os.listdir('.') if f.endswith('.laz')]
print(files)
file_split(files, node_count = 4, tile_length=None, use_lastools=False)