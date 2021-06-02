# Distributed Pipeline

## Quickstart

### 1. Set up nodes in `config`
Add nodes as `host:port`
```
[NODES]
192.168.1.2: 6938
```

### 2. Add login details in `secret`
For each node in `config` provide login details
```
[192.168.1.2]
username: ben
password: ********
```

### 3. Run 
Run the program and follow any installation prompts
```
python3 run.py point_clouds/test.laz
```

## Config

Config contains all your nodes in the form `host:port`. Known hosts can be added as well and are pulled from `~/.ssh/config`. If no port is given and the host is known, it will use the known port. Otherwise if no port is given it will default to `22`.
```
[NODES]
192.168.1.2: 6938
192.168.1.19: 8620
my_known_host:
```

## Secret

If the client key is stored in a known location such as `~/.ssh/id_rsa` this step can be skipped.

The username will default to the current session user, providing a username in the secret file will override using the session user.

Either one of password or key should be provided.

```
[192.168.1.2]
username: ben
password: ********
key: ~/.ssh/id_rsa
```

## Run 

Several libraries are required to successfully run the program. It will try and install them automatically if they are not already present. If PDAL / CloudCompare & XVFB are not installed on the remote machines, the program will exit and provide the required syntax to install them.

The following options are available when running the program

```
positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --config CONFIG       Provide an alternative config file (default: config)
  --secret SECRET       Provide an alternative secret file (default: secret)
  -o OUTPUT, --output OUTPUT
                        Output directory, will overwrite existing directory (default: ./output/)
  --tile-length TILE_LENGTH
                        If provided, splits the pointcloud into tile-length by tile-length tiles
  --cloud-compare       Use cloud compare headless to instead of pdal (default: False)
  -p PIPELINE, --pipeline PIPELINE
                        Sets the (default: pipeline.json)
  --benchmark           Loops through all available nodes and creates a report (default: False)
```