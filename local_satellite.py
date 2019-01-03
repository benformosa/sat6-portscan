#!/usr/bin/env python2
"""Check that Satellite server is listening on required ports"""

from __future__ import print_function

import argparse
import errno
import os
import socket
import subprocess
import sys
import tempfile


__author__ = "Ben Formosa"
__copyright__ = "Copyright 2018, Commonwealth of Australia"
__license__ = "GPLv3"

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


LISTENTCP = [
    80,
    443,
    5000,
    5646,
    5647,
    5671,
    8000,
    8008,
    8140,
    8443,
    9090,
]


def test_tcp():
    tested = {}
    [tested.setdefault(port) for port in LISTENTCP]
    for port in LISTENTCP:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tested[port] = False

        try:
            s.bind(("127.0.0.1", port))
            v_print(3, "Port {}: UNALLOCATED".format(port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                v_print(1, "Port {}: allocated".format(port))
                tested[port] = True
            elif e.errno == errno.EACCES:
                v_print(3, "Port {}: failed check - must be root".format(port))
            else:
                # something else raised the socket.error exception
                print(e)
        finally:
            s.close()

    failhash = {k: tested[k] for k in tested.keys() if not tested[k]}
    if len(failhash) > 0:
        v_print(3, "TCP Test failed")
        v_print(2, "The following connections failed:")
        [v_print(2, "  {}".format(port)) for port in failhash]
        return 1
    else:
        v_print(3, "Test succeeded")
        return 0


def test_tftp(server,
              port=69,
              filename='/grub2/grub.cfg',
              filehash='ec7f105c6d0ab850e56ddc0bac1c87bef4730cb52794145acba2192da1e97b70'):  # noqa
    v_print(2, "TFTP Test")
    v_print(1, "Getting file from TFTP server...")
    # Create a temporary file as the destination
    tmpfile = tempfile.mkstemp()
    tftp = ['tftp', server, str(port), '-c', 'get', filename, tmpfile[1]]
    # Attempt to get the remote file
    subprocess.call(tftp)

    # Check if destination file is not empty. Required as tftp may exit with 0
    # on error, e.g. unknown host.
    if os.stat(tmpfile[1]).st_size > 0:
        v_print(1, "Checking filehash...")
        sha = ['sha256sum', tmpfile[1]]
        shaoutput = subprocess.check_output(sha)

        if filehash == shaoutput.split()[0]:
            v_print(3, "TFTP Test succeeded")
            result = 0
        else:
            v_print(3, "TFTP Test failed - filehash doesn't match")
            result = 1
    else:
        v_print(1, "TFTP Test failed")
        result = 1

    os.remove(tmpfile[1])
    return result


def test_tftplocal(rootdir='/var/lib/tftpboot', filename='grub2/grub.cfg'):
    v_print(2, "Local TFTP Test")

    # check file exists in rootdir
    local_path = os.path.join(rootdir, filename)
    if os.path.isfile(local_path):
        # get filehash of file
        v_print(1, "Checking filehash...")
        sha = ['sha256sum', local_path]
        shaoutput = subprocess.check_output(sha)
        v_print(2, shaoutput)

        # download file with TFTP
        # verify filehash
        result = test_tftp(
            server='localhost',
            filename=filename,
            filehash=shaoutput.split()[0]
        )
    else:
        v_print(3, "TFTP FAIL - local file doesn't exist")
        result = 1

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--skip-tftp',
        action='store_true',
        help="Skip TFTP test"
    )
    parser.add_argument(
        '-v', '--verbosity',
        action="count",
        help="Increase output verbosity (e.g., -vv is more than -v)"
    )
    args = parser.parse_args()

    # Set up v_print function for verbose output
    if args.verbosity:
        def _v_print(*verb_args):
            if verb_args[0] > (3 - args.verbosity):
                print(verb_args[1])
    else:
        # do-nothing function
        def _v_print(*a): return None

    global v_print
    v_print = _v_print

    result = 0
    result += test_tcp()
    if not args.skip_tftp:
        result += test_tftplocal()
    sys.exit(result)


if __name__ == '__main__':
    main()
