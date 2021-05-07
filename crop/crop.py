import os
from pathlib import Path
import subprocess
import sys
from typing import Iterator

import fileinput

# install pdal
def crop(files):
    for file in files:
        if file.endswith('.laz'):
            result = subprocess.check_output(["pdal", "info", file])
            #find minx
            start = str(result).find('minx')
            if start == -1:
                print('Count not found minx in {file}')
            else:
                end = str(result).find(',', start)
                minx = str(result)[start+6:end]

                #find maxx
                start = str(result).find('maxx')
                if start == -1:
                    print('Count not found maxx in {file}')
                else:
                    end = str(result).find(',', start)
                    maxx = str(result)[start+6:end]

                #find miny
                start = str(result).find('miny')
                if start == -1:
                    print('Count not found miny in {file}')
                else:
                    end = str(result).find(',', start)
                    miny = str(result)[start+6:end]
                print(f"minx is {float(maxx)}")
                print(f"maxx is {float(minx)}")
                length = float(maxx) - float(minx)
                # crop
                new_length = length*(10/11)
                print(f"{file} had x-axis length{length}, this is cropped to {new_length}")

            #replace strings in crop.json
            for file2 in files:

                if file2 == 'crop.json':

                    #subprocess.run(["sed", f"'s/1/{str(minx)} {str(miny)}/g'", file])
                    #subprocess.run(["sed", "-e", "s/1/" + "POINT(" + str(minx) + " " + str(miny) + ")/g", file, "&&", "sed", "-e", "s/2/" + str(new_length) + "/g" , file, "&&", "sed", "-e", "s/0/" + file + "/g", file])
                    subprocess.run(["sed", "-i", "s/one/" + "POINT(" + str(minx) + " " + str(miny) + ")/", file2])
                    subprocess.run(["sed", "-i", "s/two/" + str(new_length) + "/", file2])
                    subprocess.run(["sed", "-i", "s/zero/" + file + "/", file2])
                    print(file2 + ":")
                    subprocess.run(["cat", file2])

                    # run the crop
                    subprocess.run(["pdal", "pipeline", file])
                    print("pdal crop done")

                    #recreate crop.json to be back at original state
                    subprocess.run(["rm", "crop.json"])
                    subprocess.run(["cp", "cropbackup.json", "crop.json"])

crop(['test.laz', 'crop.json'])