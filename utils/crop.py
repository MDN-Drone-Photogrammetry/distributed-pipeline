import os
from pathlib import Path
import subprocess
import sys
from typing import Iterator


#this code heavily relies on the output format of "pdal info <>:"
def crop(files):
    for file in files:
        if file.endswith('.laz'):
            result = subprocess.check_output(["pdal", "info", file])
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

                #find minz
                start = str(result).rfind('minz')
                if start == -1:
                    print('Count not found minz in {file}')
                else:
                    end = str(result).find('\\n', start)
                    minz = str(result)[start+6:end]

                #find maxz
                start = str(result).rfind('maxz')
                if start == -1:
                    print('Count not found maxz in {file}')
                else:
                    end = str(result).find(',', start)
                    maxz = str(result)[start+6:end]

                print(f"minx is {float(minx)}")
                print(f"maxx is {float(maxx)}")
                print(f"miny is {float(miny)}")
                print(f"maxy is {float(maxy)}")
                print(f"minz is {float(minz)}")
                print(f"maxz is {float(maxz)}")
                lengthX = float(maxx) - float(minx)
                lengthY = float(maxy) - float(miny)
                lengthZ = float(maxz) - float(minz)
                lengthMax = 0
                # check which axis of the point cloud has the longest length
                if lengthX > lengthY and lengthX > lengthZ:
                    lengthMax = lengthX
                elif lengthY > lengthZ:
                    lengthMax = lengthY 
                else:
                    lengthMax = lengthZ

                # define the length to be croped 
                new_length = lengthMax*(10/11)
                print(f"Point cloud in {file} has length {lengthMax}, this is cropped to {new_length}")

            #replace strings in cropBound.json
            for file2 in files:

                if file2 == 'cropBound.json':

                    
                    subprocess.run(["sed", "-i", "s/zero/" + file + "/", file2])
                    subprocess.run(["sed", "-i", "s/one/"+"["+str(minx)+", "+str(float(minx)+float(new_length))+"],["+str(miny)+", "+str(float(miny)+float(new_length))+"],["+str(minz)+", "+str(float(minz)+float(new_length))+"]/", file2])
                    
                    print(file2 + ":")
                    subprocess.run(["cat", file2])

                    # run the crop
                    subprocess.run(["pdal", "pipeline", file2])
                    print("pdal crop done")

                    #recreate crop.json to be back at original state
                    subprocess.run(["rm", "cropBound.json"])
                    subprocess.run(["cp", "cropBoundbackup.json", "cropBound.json"])



