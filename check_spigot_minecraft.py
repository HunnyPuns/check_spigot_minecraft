#!/usr/bin/env python3

#
# check_minecraft.py created by HunnyPuns on January 4th, 2021
# GitHub: https://github.com/HunnyPuns/

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# GPL v3: https://www.gnu.org/licenses/gpl-3.0.html
#

import argparse
import subprocess
import sys

returnusercount = -1
returnmaxcount = -1

returntps = ''
returnmem = ''

#0 = OK, 1 = WARNING, 2 = CRITICAL, 3 and greater = UNKNOWN
#The script must prove that everything is OK, else it is UNKNOWN.
status = 3

parser = argparse.ArgumentParser()
parser.add_argument('-H',
                    '--host',
                    required=(),
                    type=str,
                    help='IP address of the Minecraft server')
parser.add_argument('-p',
                    '--password',
                    required=True,
                    type=str,
                    help='rcon password for the Minecraft server')
parser.add_argument('-P',
                    '--port',
                    required=False,
                    type=str,
                    default='25575',
                    help='rcon port for the Minecraft server')
parser.add_argument('-l',
                    '--list',
                    required=False,
                    type=bool,
                    help='List the number of players on the server')
parser.add_argument('-m',
                    '--mcrcon',
                    required=False,
                    type=str,
                    default='/usr/bin/env mcrcon',
                    help='Path to the mcrcon binary, including binary name.')
parser.add_argument('-w',
                        '--warning',
                        required=False,
                        type=int,
                        help='Set the warning threshold')
parser.add_argument('-c',
                        '--critical',
                        required=False,
                        type=int,
                        help='Set the critical threshold')

subparsers = parser.add_subparsers(help='sub-command help', dest='command')

parser_tps = subparsers.add_parser('tps',
                                    help='Monitor TPS and/or memory utilization')
parser_tps.add_argument('-k',
                        '--key',
                        required=False,
                        type=str,
                        choices=['tps','memory'],
                        help='Set the key metric. e.g. tps or memory')

args = parser.parse_args(sys.argv[1:])

resultstring = 'Nothing changed the result string'

if (args.list is None and args.key == 'memory'):
    try:
        tpsdata = subprocess.run([args.mcrcon, "-H", args.host, "-P", args.port, "-p", args.password, "-c", "tps"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Hit CalledProcessError. Typically this means the script could not connect to the server.")
        sys.exit(3)

    returnmem = str(tpsdata.stdout).split(" ")[11]
    usedmem = int(returnmem.split('/')[0])
    maxmem = int(returnmem.split('/')[1])
    resultstring = 'Memory: {0} used of {1} max | used_mem={0}; max_mem={1}'.format(usedmem, maxmem)

    if (args.critical is not None and usedmem > args.critical):
        status = 2
    elif (args.warning is not None and usedmem > args.warning):
        status = 1
    else:
        status = 0


elif (args.list is None and args.key == 'tps'):
    try:
        tpsdata = subprocess.run([args.mcrcon, "-H", args.host, "-P", args.port, "-p", args.password, "-c", "tps"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Hit CalledProcessError. Typically this means the script could not connect to the server.")
        sys.exit(3)

    if (args.key == 'tps' and args.critical is not None and args.warning is not None):
        if (args.warning < args.critical):
            resultstring = 'When alerting on TPS, lower is worse. Warning should be a higher number than critical.'
            status = 3

            print(resultstring)
            sys.exit(status)

    returntps = str(tpsdata.stdout).split("\n")[0]

    if ('*' in returntps):
        len1m = len(str(returntps).split(' ')[6]) - 1
        len5m = len(str(returntps).split(' ')[7]) - 1
        len15m = len(str(returntps).split(' ')[8]) - 10
        tps1m = float(str(returntps).split(' ')[6][1:len1m])
        tps5m = float(str(returntps).split(' ')[7][1:len5m])
        tps15m = float(str(returntps).split(' ')[8][1:len15m])

        resultstring = 'tps times were {0}, {1}, {2}|tps_1minute={0}; tps_5minute={1}; tps_15minute={2}'.format(tps1m, tps5m, tps15m)

    else:
        len1m = len(str(returntps).split(' ')[6]) - 1
        len5m = len(str(returntps).split(' ')[7]) - 1
        len15m = len(str(returntps).split(' ')[8]) - 10
        tps1m = float(str(returntps).split(' ')[6][0:len1m])
        tps15m = float(str(returntps).split(' ')[7][0:len5m])
        tps5m = float(str(returntps).split(' ')[8][0:len15m])

        resultstring = 'tps times were {0}, {1}, {2}|tps_1minute={0}; tps_5minute={1}; tps_15minute={2}'.format(tps1m, tps5m, tps15m)

    if (args.critical is not None and tps15m < args.critical):
        status = 2
    elif (args.warning is not None and tps15m < args.warning):
        status = 1
    else:
        status = 0

elif (args.list is True):
    try:
        userlist = subprocess.run([args.mcrcon, "-H", args.host, "-P", args.port, "-p", args.password, "-c", "list"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Hit CalledProcessError. Typically this means the script could not connect to the server.")
        sys.exit(3)

    returnusercount = str(userlist.stdout).split(" ")[2]
    returnmaxcount = str(userlist.stdout).split(" ")[7]
    status = 0
    resultstring = '{0} users of {1} connected.|current_users={0}; max_users={1}'.format(returnusercount, returnmaxcount)

print(resultstring)
sys.exit(status)
