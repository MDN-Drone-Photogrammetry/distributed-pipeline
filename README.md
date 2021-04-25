# distributed-pipeline

## Quickstart

### 1. Install PDAL on main machine

```
sudo apt install pdal
```

### 2. Repeat above for any node machines

### 3. Modify `config`

Change the hosts and ports to your node machines. Ports are optional as they are used with RPyC.

```
[NODES]
192.168.1.2: 6938
192.168.1.19: 8620
```

### 4. Create a `secret` file

Create a secret file to include the login details to your node machine. If the machine is already in your hosts file and the key-pair added to the current machine, the address is all that is required.

```
[192.168.1.2]
ssh-port: 2940
username: ben
password: ********
key: ~/.ssh/id_rsa
```

### 5. Run!

Run the

```
python3 run.py point_clouds/*
```
