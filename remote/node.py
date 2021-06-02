import configparser
from typing import Iterator
from utils.utils import colorstr
from utils.timer import Timer

import asyncssh

from pathlib import Path
import os

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.remote_path = "remote-pipeline/"
        self.output_path = f"{self.remote_path}output/"
        self.files = None

        self.username = None
        self.key = None
        self.password = None

        self.get_secrets()

        self.conn = None  # for asyncSSH

    def get_secrets(self):
        secrets = configparser.ConfigParser()
        secrets.read('secret')
        
        if  self.host not in secrets:
            print(f"Node {self.host} does not have a secret")
            return

        try:
            if "port" in secrets[self.host]:
                self.ssh_port = secrets[self.host]["port"]
            else:
                self.ssh_port = 22

            self.username = secrets[self.host]["username"]
            if "key" in secrets[self.host]:
                self.key = secrets[self.host]["key"]
            elif "password" in secrets[self.host]:
                self.password = secrets[self.host]["password"]
        except:
            print(f"Node {self.host} secret could not be read properly")

    async def setup(self, use_cloud_compare=False):
        print(f"Connecting to node {self.host}...")
        self.use_cloud_compare = use_cloud_compare

        # try:
        await self.connect()
        # except:
        #     print(colorstr('red', "Could not connect to host"))
        #     return False

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

    async def remote_exec(self, pipeline=None):
        for file in self.files:
            file_name = file.split('/')[-1]
            if (file_name == pipeline):
                continue

            print(f"Started processing {file_name} on {self.host} with {'CloudCompare' if self.use_cloud_compare else 'PDAL'}")
            file_timer = Timer(name="file", logger=None, )
            file_timer.start()

            if self.use_cloud_compare:
                response = await self.conn.run(
                    f'xvfb-run cloudcompare.CloudCompare -SILENT  -O {self.remote_path}{file_name} -COMPUTE_NORMALS -CURV GAUSS 0.25')
                await self.conn.run(
                    f'mv {self.remote_path}{file_name} {self.output_path}{file_name}')       
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
        await asyncssh.scp((self.conn, self.output_path+'*'), output, preserve=True, recurse=True)

    async def connect(self):
        known_hosts = Path.home().joinpath('.ssh','config')
        asyncssh.read_known_hosts([known_hosts])
        
        if self.key is not None:
            key = asyncssh.read_private_key(Path(self.key).expanduser())
        
        port = int(self.port) if self.port is not '' else ()
        username = self.username if self.username is not None else ()
        keys = [key] if self.key is not None else ()

        self.conn = await asyncssh.connect(self.host, username=username, port=port, client_keys=keys)

    async def has_pdal(self):
        assert self.conn is not None, "SSH must be intialised before PDAL can be tested for"

        # stdin, stdout, stderr = self.ssh.exec_command('which pdal')
        result = await self.conn.run('which pdal')
        lines = result.stdout
        # lines = stdout.readlines()
        if len(lines) == 0:
            print(
                f"PDAL not installed on {self.host}, please install on the node machine with (debian)\n\n{colorstr('bold','sudo apt install pdal')}\n")
            return False
        else:
            return True

    async def has_cloud_compare(self):
        assert self.conn is not None, "SSH must be intialised before PDAL can be tested for"

        result = await self.conn.run('which cloudcompare.CloudCompare')
        cloudcompare = len(result.stdout) > 0
        result = await self.conn.run('which xvfb-run')
        xvfb = len(result.stdout) > 0

        success = True
        if not cloudcompare:
            print(
                f"CloudCompare not installed on {self.host}, please install on the node machine with (debian)\n\n{colorstr('bold','sudo snap install cloudcompare')}\n")
            success =  False
        
        if not xvfb:
            print(
                f"xvfb not installed on {self.host}, please install on the node machine with (debian)\n\n{colorstr('bold','sudo apt-get install xvfb')}\n")
            success =  False

        return success
