# Satellite 6 Portscan

A set of scripts to test network connectivity between Red Hat Satellite 6 servers and clients.

Based on [Red Hat Satellite 6.3 List of Network Ports](https://access.redhat.com/solutions/3382741) and [Red Hat Satellite 6.3 Communication Matrix (PDF)](https://access.redhat.com/sites/default/files/attachments/satellite_6_communication_matrix_satellite_6.3_16march2018.pdf).

## What the script does

### `local_satellite.py`

* Checks if the TCP ports required for clients are allocated to processes on the local system.
* Checks the hash of the file '/var/lib/tftpboot/grub2/grub.cfg/
* Attempts to download the file 'grub2/grub.cfg' via TFTP from localhost, and verifies the file's hash.

### `client_to_satellite.py`

* Tests the TCP connectivity required for a Satellite client by attempting to connect to each on the specified server.
* Attempts to download the file 'grub2/grub.cfg' via TFTP from the specified server, and verifies the file's hash.

## What versions does it work on

* Satellite 6.3
* Satellite 6.4

## Requirements

* A TFTP client, available in $PATH. I've tested with [tftp-hpa](https://git.kernel.org/pub/scm/network/tftp/tftp-hpa.git), available from the RHEL software repo.
  * `yum install tftp`

## Usage

### `local_satellite.py`

To test that a Satellite server has ports open and TFTP configured:

```bash
./local_satellite.py
```

#### Example Output

```
$ sudo ./sat6_portscan_local_satellite.py -vvv
Port 443: allocated
Port 5000: allocated
Port 5646: allocated
Port 5647: allocated
Port 5671: allocated
Port 80: allocated
Port 8000: UNALLOCATED
Port 8008: allocated
Port 8140: allocated
Port 8443: allocated
Port 9090: allocated
TCP Test failed
The following connections failed:
  8000
Local TFTP Test
Checking filehash...
ec7f105c6d0ab850e56ddc0bac1c87bef4730cb52794145acba2192da1e97b70  /var/lib/tftpboot/grub2/grub.cfg

TFTP Test
Getting file from TFTP server...
Checking filehash...
TFTP Test succeeded
```

### `client_to_satellite.py`

To test that a system can connect to the required ports and TFTP on a Satellite server.  
You must specify the hostname of the Satellite server.

```bash
./client_to_satellite.py HOSTNAME
```

#### Example Output

```
$ ./client_to_satellite.py satellite.example.com -vvv
TCP Test
satellite.example.com:8000 FAIL - [Errno 111] Connection refused
satellite.example.com:9090 OK
satellite.example.com:8443 OK
satellite.example.com:5000 OK
satellite.example.com:8140 OK
satellite.example.com:5647 OK
satellite.example.com:80 OK
satellite.example.com:443 OK
TCP Test failed
The following connections failed:
  satellite.example.com:8000
TFTP Test
Getting file from TFTP server...
Checking filehash...
TFTP Test succeeded
```

### General

* On a successful test, the exit code will be 0.
* For more output, use the verbose option, `-v[v][v]` 
* The TFTP test can be skipped on both commands with the `--skip-tftp` option.
