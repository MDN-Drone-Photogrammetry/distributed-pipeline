import configparser
from typing import Iterator
from utils.utils import colorstr
from utils.timer import Timer

import asyncssh

from pathlib import Path


class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.remote_path = "remote-pipeline/"
        self.output_path = f"{self.remote_path}output/"
        self.files = None

        self.ssh_port = None
        self.username = None
        self.key = None
        self.password = None

        self.get_secrets()

        self.conn = None  # for asyncSSH

    def get_secrets(self):
        secrets = configparser.ConfigParser()
        secrets.read('secret')

        try:
            self.ssh_port = secrets[self.host]["ssh-port"]
            self.username = secrets[self.host]["username"]
            if "key" in secrets[self.host]:
                self.key = secrets[self.host]["key"]
            elif "password" in secrets[self.host]:
                self.password = secrets[self.host]["password"]
        except:
            print(f"Node {self.host} does not have a secret")

    async def setup(self, use_cloud_compare=False):
        print(f"Connecting to node {self.host}...")
        try:
            await self.connect()
        except:
            print(colorstr('red', "Could not connect to host"))
            return False

        if use_cloud_compare:
            if not await self.has_cloud_compare():
                print(colorstr('red', "Node did not setup correctly"))
                return False        
        else:
            if not await self.has_pdal():
                print(colorstr('red', "Node did not setup correctly"))
                return False

        # Clean up the node from previous runs, get will retreive all files from
        await self.clean_up()


        print(colorstr('green', f"Connected to node {self.host}"))
        return True

    async def put(self, files: Iterator[Path]):
        assert self.conn is not None, "SSH must be intialised before files can be transferred"

        await self.conn.run(f'mkdir {self.remote_path}')
        await self.conn.run(f'mkdir {self.output_path}')

        await asyncssh.scp(files, (self.conn, self.remote_path), preserve=True, recurse=True)

        self.files = files
        print(
            f"Transferred {len(files)} file(s) to {self.host}:~/{self.remote_path}")

    async def remote_exec(self, pipeline=None, use_cloud_compare=False):
        for file in self.files:
            file_name = file.split('/')[-1]
            if (file_name == pipeline):
                continue

            print(f"Started processing {file_name} on {self.host}")
            file_timer = Timer(name="file", logger=None, )
            file_timer.start()

            if use_cloud_compare:
                response = await self.conn.run(
                    f'xvfb-run cloudcompare.CloudCompare -SILENT  -O {self.remote_path}{file_name} -COMPUTE_NORMALS -CURV GAUSS 0.25')
            else:
                response = await self.conn.run(
                    f'pdal pipeline {self.remote_path}/{pipeline} --readers.las.filename={self.remote_path}{file_name} --writers.las.filename={self.output_path}{file_name}')

            errors = response.stderr
            if len(errors) > 0:
                print(
                    colorstr('red', f"Errors while processing on {self.host}:"))
                print(errors)
            time = file_timer.stop()
            print(
                f"Finished processing {file_name} on {self.host} in {time:.2f} seconds")

    async def clean_up(self):
        assert self.conn is not None, "SSH must be intialised before files can be cleaned up"
        result = await self.conn.run(f'rm -r {self.remote_path}')

    async def get(self, output):
        assert self.conn is not None, "SSH must be intialised before files can be retrieved"
        # if self.output_path[-1]
        print(self.output_path)
        await asyncssh.scp((self.conn, self.output_path+'*'), output, preserve=True, recurse=True)

    async def connect(self):
        asyncssh.read_known_hosts([Path('~/.ssh/config').expanduser()])
        if self.key is not None:
            asyncssh.read_private_key([Path(self.key).expanduser()])
        self.conn = await asyncssh.connect(self.host, port=int(self.ssh_port) if self.ssh_port else ())

    async def has_pdal(self):
        assert self.conn is not None, "SSH must be intialised before PDAL can be tested for"

        # stdin, stdout, stderr = self.ssh.exec_command('which pdal')
        result = await self.conn.run('which pdal')
        lines = result.stdout
        # lines = stdout.readlines()
        if len(lines) == 0:
            print(
                f"PDAL not installed, please install on the node machine with (debian)\n\n{colorstr('bold','sudo apt install pdal')}\n")
            return False
        else:
            return True

    async def has_cloud_compare(self):
        assert self.conn is not None, "SSH must be intialised before PDAL can be tested for"

        # stdin, stdout, stderr = self.ssh.exec_command('which pdal')
        result = await self.conn.run('which cloudcompare.CloudCompare')
        cloudcompare = len(result.stdout) > 0
        result = await self.conn.run('which xvfb-run')
        xvfb = len(result.stdout) > 0

        success = True
        # lines = stdout.readlines()
        if not cloudcompare:
            print(
                f"CloudCompare not installed, please install on the node machine with (debian)\n\n{colorstr('bold','sudo snap install cloudcompare')}\n")
            success =  False
        
        if not xvfb:
            print(
                f"xvfb not installed, please install on the node machine with (debian)\n\n{colorstr('bold','sudo apt-get install xvfb')}\n")
            success =  False

        return success
