import os
from pathlib import Path
import subprocess
import sys
from typing import Iterator

def crop(files):
    paths = []
    for file in files:
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
            
                length = float(maxx) - float(minx)
                # crop
                new_length = length*(10/11)
                print(f"{file} had x-axis length{length}, this is cropped to {new_length} tiles")

                #run crop.json
                if file == 'crop.json':
                    with open(file, 'w+') as file:
                        content = file.read()
                        file.seek(0)
                        content.replace('minx', minx)
                        content.replace('miny', miny)
                        content.replace('length', new_length)
                        file.write(content)

                    subprocess.run(["pdal", "pipeline", file])
                    print("pdal crop done")


# path = os.getcwd()
# print(path)
crop(['./test.laz'])
    #from pdal info
    #find minx, maxx, miny
    #calculate length
    #calculate new length