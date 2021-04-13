import configparser
from typing import Iterator

import paramiko
from scp import SCPClient

from pathlib import Path

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ssh_port = None
        self.username = None
        self.key = None
        self.password = None
        
        self.get_secrets()

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

    def setup(self, files: Iterator[Path]):
        print(f"Connecting to node {self.host}...")
        self.connect()
        
        scp = SCPClient(self.ssh.get_transport())
        # remote_path = f'/home/{self.username}/distributed_pipeline/'
        scp.put(files)#, recursive=True, remote_path=remote_path)

        scp.close()

        print(f"Success! transferred {len(files)} files\n")

    def remote_exec(self):

        print("THIS IS WHERE WE ADD SOMETHING :)")
        # stdin, stdout, stderr = selfssh.exec_command(f'ls {remote_path}/')

        # lines = stdout.readlines()

        # print(lines)

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        
        if self.key == None and self.password == None:
            self.ssh.connect(self.host,  self.ssh_port, self.username)
        if self.key != None: # Connect to the host preferring keys over passwords
            key_path = Path(self.key)
            key = paramiko.RSAKey.from_private_key_file(key_path.expanduser())
            self.ssh.connect(self.host,  self.ssh_port, self.username, pkey=key)
        else:
            self.ssh.connect(self.host,  self.ssh_port, self.username, self.password)