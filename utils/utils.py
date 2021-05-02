import os
from pathlib import Path
import subprocess
import platform
import socket
import configparser
from typing import Iterator
from utils.colorstr import colorstr
from remote.node import Node
import sys

    # tools = ['pdal']
    # for tool in tools:
    #     check = is_tool(tool)
    #     if not check:
    #         print(
    #             f"{tool} must be installed to continue, this can be installed using\n\nsudo apt install {tool}")
    #         sys.exit()

def check_requirements(requirements='requirements.txt', exclude=()):
    # Check installed dependencies meet requirements (pass *.txt file or list of packages)
    import pkg_resources as pkg
    prefix = colorstr('red', 'bold', 'requirements:')
    if isinstance(requirements, (str, Path)):  # requirements.txt file
        file = Path(requirements)
        if not file.exists():
            print(f"{prefix} {file.resolve()} not found, check failed.")
            return
        requirements = [f'{x.name}{x.specifier}' for x in pkg.parse_requirements(
            file.open()) if x.name not in exclude]
    else:  # list or tuple of packages
        requirements = [x for x in requirements if x not in exclude]

    n = 0  # number of packages updates
    for r in requirements:
        try:
            pkg.require(r)
        except Exception as e:  # DistributionNotFound or VersionConflict if requirements not met
            n += 1
            print(
                f"{prefix} {e.req} not found and is required by distributed-pipeline, attempting auto-update...")
            print(subprocess.check_output(
                f"pip3 install '{e.req}'", shell=True).decode())

    if n:  # if packages updated
        source = file.resolve() if 'file' in locals() else requirements
        s = f"{prefix} {n} package{'s' * (n > 1)} updated per {source}\n" \
            f"{prefix} ⚠️ {colorstr('bold', 'Restart runtime or rerun command for updates to take effect')}\n"
        print(emojis(s))  # emoji-safe

    tools = ['pdal']
    for tool in tools:
        check = is_tool(tool)
        if not check:
            print(
                f"{tool} must be installed to continue, this can be installed using\n\nsudo apt install {tool}")
            sys.exit()


def emojis(str=''):
    # Return platform-dependent emoji-safe version of string
    return str.encode().decode('ascii', 'ignore') if platform.system() == 'Windows' else str


def valid_address(netloc):
    try:
        socket.gethostbyname(netloc)
        return True
    except:
        return False


def get_nodes() -> Iterator[Node]:
    config = configparser.ConfigParser()
    config.read('config')

    nodes = []
    print(f"Found {len(config['NODES'])} nodes in config:\n")

    for key in config['NODES']:
        port = config['NODES'][key]
        print(f"Node {key}")
        try:
            nodes.append(Node(key, port))
        except:
            print(f"Exception, skipping node {key}")
        print("")

    return nodes


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

async def transfer_files(files: Iterator[Path], pipeline, nodes):
    split_files = []

    for file in files:
        path = os.path.join(file.parent, 'split') 
        splits = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        split_files.extend(splits)
        
    split_files = chunkIt(split_files, len(nodes))
    
    for i in range(len(nodes)):
        node_files = split_files[i]
        node_files.append(pipeline)

        await nodes[i].put(node_files)