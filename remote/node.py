import configparser

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

    def setup(self):
        print(f"Connecting to node {self.host}...")
        ssh = self.connect()

        scp = SCPClient(ssh.get_transport())
        # ssh.scp
        print("Success!\n")

    def connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        
        if self.key == None and self.password == None:
            ssh.connect(self.host,  self.ssh_port, self.username)
        if self.key != None: # Connect to the host preferring keys over passwords
            key_path = Path(self.key)
            key = paramiko.RSAKey.from_private_key_file(key_path.expanduser())
            ssh.connect(self.host,  self.ssh_port, self.username, pkey=key)
        else:
            ssh.connect(self.host,  self.ssh_port, self.username, self.password)

        return ssh