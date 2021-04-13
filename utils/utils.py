from pathlib import Path
import subprocess
import platform
import socket
import configparser
from typing import Iterator
from remote.node import Node
import random
import sys


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
                f"pip install '{e.req}'", shell=True).decode())

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


def colorstr(*input):
    # Colors a string https://en.wikipedia.org/wiki/ANSI_escape_code, i.e.  colorstr('blue', 'hello world')
    # color arguments, string
    *args, string = input if len(input) > 1 else ('blue', 'bold', input[0])
    colors = {'black': '\033[30m',  # basic colors
              'red': '\033[31m',
              'green': '\033[32m',
              'yellow': '\033[33m',
              'blue': '\033[34m',
              'magenta': '\033[35m',
              'cyan': '\033[36m',
              'white': '\033[37m',
              'bright_black': '\033[90m',  # bright colors
              'bright_red': '\033[91m',
              'bright_green': '\033[92m',
              'bright_yellow': '\033[93m',
              'bright_blue': '\033[94m',
              'bright_magenta': '\033[95m',
              'bright_cyan': '\033[96m',
              'bright_white': '\033[97m',
              'end': '\033[0m',  # misc
              'bold': '\033[1m',
              'underline': '\033[4m'}
    return ''.join(colors[x] for x in args) + f'{string}' + colors['end']


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
        if (valid_address(key)):
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

        else:
            print(f"Address {key} is not valid")
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