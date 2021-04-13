from pathlib import Path
import subprocess
import platform
import socket
import configparser
from typing import Iterator
from remote.node import Node
import random

    # tools = ['pdal']
    # for tool in tools:
    #     check = is_tool(tool)
    #     if not check:
    #         print(
    #             f"{tool} must be installed to continue, this can be installed using\n\nsudo apt install {tool}")
    #         sys.exit()

def get_nodes() -> Iterator[Node]:
    config = configparser.ConfigParser()
    config.read('config')

    nodes = []
    print(f"Found {len(config['NODES'])} nodes in config:\n")

    for key in config['NODES']:
        # if (valid_address(key)): # Don't check valid address as may use the hosts file
        port = config['NODES'][key]
        generated = ''
        if port == '':
            # Generates a random port in the user assignable range
            port = random.randint(1024, 49151)
            generated = ' (generated)'
        print(f"Node {key} on port {port}{generated}")
        try:
            nodes.append(Node(key, port))
        except:
            print(f"Exception, skipping node {key}")
        print("")

        # else:
        #     print(f"Address {key} is not valid")
    return nodes


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None


def transfer_files(files, nodes):
    for i in range(len(nodes)):
        split_files = []
        for file in files:
            name_split = file.name.split('.')
            new_name = f'{name_split[0]}_{i+1}.{name_split[1]}'
            split_path = Path.joinpath(file.parents[0], 'split', new_name)
            split_files.append(str(split_path.absolute()))
        nodes[i] 
        nodes[i].setup(split_files)