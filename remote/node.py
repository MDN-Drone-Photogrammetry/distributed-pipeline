import configparser
import os
from typing import Iterator
from utils.utils import colorstr

import paramiko
import asyncssh
from scp import SCPClient

from pathlib import Path


class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.remote_path = "remote-pipeline/"
        self.output_path = f"{self.remote_path}output/"
        self.files = None

        self.ssh = None
        self.ssh_port = None
        self.username = None
        self.key = None
        self.password = None

        self.get_secrets()

        self.conn = None # for asyncSSH

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
            print(f"Node {self.host} does not have a valid secret")
            raise Exception()

    async def setup(self):
        print("----------------------------------")
        print(f"Connecting to node {self.host}...")
        await self.connect()

        if not await self.has_pdal():
            print(colorstr('red', "Node did not setup correctly"))
            return False

        print(colorstr('green', "Connected\n"))
        return True

    async def put(self, files: Iterator[Path]):
        assert self.conn is not None, "SSH must be intialised before files can be transferred"

        await self.conn.run(f'mkdir {self.remote_path}')
        await self.conn.run(f'mkdir {self.output_path}')

        # await self.conn.run(f'mkdir {self.output_path}')

        # shutil
        # scp uname@server1:/path/to/dir/file[1-2] .
        await asyncssh.scp(files, (self.conn, self.remote_path), preserve=True, recurse=True)
        # scp = SCPClient(self.ssh.get_transport())
        # scp.put(files, recursive=True, remote_path=self.remote_path)
        # scp.close()

        self.files = files
        print(
            f"Transferred {len(files)} file(s) to {self.host}:~/{self.remote_path}")

    async def remote_exec(self):
        
        print(f"Executing pdal translate on {self.host}")
        for file in self.files:
            file_name = file.split('/')[-1]
            stdin, stdout, stderr = self.ssh.exec_command(
                f'pdal translate {self.remote_path}{file_name} {self.output_path}{file_name} -f filters.normal')
            # lines = stdout.readlines()
            errors = stderr.readlines()
            if len(errors) > 0:
                print(
                    colorstr('red', f"Errors while processing on {self.host}:"))
                print(errors)

    def clean_up(self):
        assert self.conn is not None, "SSH must be intialised before files can be cleaned up"

    def get(self):
        assert self.conn is not None, "SSH must be intialised before files can be retrieved"
        scp = SCPClient(self.ssh.get_transport())

    async def connect(self):
        # self.ssh = paramiko.SSHClient()
        # self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # self.ssh.load_system_host_keys()
        # self.ssh = asyncssh.SSHAgentClient('~')#Path('~/.ssh').expanduser())
        # key_path = Path(self.key)
        # keys = await self.ssh.get_keys()
        # self.ssh.
        # print(keys)

        # asyncssh.read_known_hosts([Path('~/.ssh/config').expanduser()])
        # asyncssh.read_authorized_keys([Path('~/.ssh/id_rsa').expanduser()])
        self.conn = await asyncssh.connect(self.host, int(self.port))
        # if self.key == None and self.password == None:
        #     self.ssh.connect(self.host,  self.ssh_port, self.username)
        #     self.conn = asyncssh.connect(self.host,  self.ssh_port, self.username)
        # if self.key != None:  # Connect to the host preferring keys over passwords
        #     key_path = Path(self.key)
        #     key = paramiko.RSAKey.from_private_key_file(key_path.expanduser())
        #     self.ssh.connect(self.host,  self.ssh_port,
        #                      self.username, pkey=key)
        # else:
        #     self.ssh.connect(self.host,  self.ssh_port,
        #                      self.username, self.password)

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
