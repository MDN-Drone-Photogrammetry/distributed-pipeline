import configparser
import os
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

        if self.host in secrets.sections():
            try:
                if "ssh-port" in secrets[self.host]:
                    self.ssh_port = secrets[self.host]["ssh-port"]
                if "username" in secrets[self.host]:
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
        scp.put(files)  # , recursive=True, remote_path=remote_path)

        scp.close()

        print(f"Success! transferred {len(files)} files\n")

    def remote_exec(self):

        print("THIS IS WHERE WE ADD SOMETHING :)")
        # stdin, stdout, stderr = selfssh.exec_command(f'ls {remote_path}/')

        # lines = stdout.readlines()

        # print(lines)

    def connect(self):
        # ssh_config = paramiko.SSHConfig()
        # user_config_file = os.path.expanduser("~/.ssh/config")
        # if os.path.exists(user_config_file):
        #     with open(user_config_file) as f:
        #         ssh_config.parse(f)

        # cfg = {'hostname': options['hostname'], 'username': options["username"]}

        # user_config = ssh_config.lookup(cfg['hostname'])
        # for k in ('hostname', 'username', 'port'):
        #     if k in user_config:
        #         cfg[k] = user_config[k]

        # if 'proxycommand' in user_config:
        #     cfg['sock'] = paramiko.ProxyCommand(user_config['proxycommand'])

        # client.connect(**cfg)
        
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        # self.ssh.load

        if self.key == None and self.password == None and self.username == None:
            self.ssh.connect(self.host)
        elif self.key == None and self.password == None:
            self.ssh.connect(self.host,  self.ssh_port, self.username)
        elif self.key != None:  # Connect to the host preferring keys over passwords
            key_path = Path(self.key)
            key = paramiko.RSAKey.from_private_key_file(key_path.expanduser())
            self.ssh.connect(self.host,  self.ssh_port,
                             self.username, pkey=key)
        else:
            self.ssh.connect(self.host,  self.ssh_port,
                             self.username, self.password)
