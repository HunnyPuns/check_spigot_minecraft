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
                    default='/usr/local/nagios/libexec/mcrcon',
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
    tpsdata = subprocess.getoutput('{0} -H {1} -P {2} -p {3} -c "tps"'.format(args.mcrcon,
                                                                            args.host,
                                                                            args.port,
                                                                            args.password))

    returnmem = tpsdata.split("\n")[1]
    usedmem = int(returnmem.split('/')[0].split(' ')[3])
    maxmem = int(returnmem.split('/')[1].split(' ')[3])
    resultstring = 'Memory: {0} used of {1} max | used_mem={0}; max_mem={1}'.format(usedmem, maxmem)

    if (args.critical is not None and usedmem > args.critical):
        status = 2
    elif (args.warning is not None and usedmem > args.warning):
        status = 1
    else:
        status = 0


elif (args.list is None and args.key == 'tps'):
    tpsdata = subprocess.getoutput('{0} -H {1} -P {2} -p {3} -c "tps"'.format(args.mcrcon,
                                                                            args.host,
                                                                            args.port,
                                                                            args.password))

    if (args.key == 'tps' and args.critical is not None and args.warning is not None):
        if (args.warning < args.critical):
            resultstring = 'When alerting on TPS, lower is worse. Warning should be a higher number than critical.'
            status = 3

            print(resultstring)
            sys.exit(status)

    returntps = tpsdata.split("\n")[0]
    tps1m = float(returntps.split(':')[1].split(' *')[1][0:4])
    tps5m = float(returntps.split(':')[1].split(' *')[2][0:4])
    tps15m = float(returntps.split(':')[1].split(' *')[3][0:4])
    resultstring = 'tps times were {0}, {1}, {2}|tps_1minute={0}; tps_5minute={1}; tps_15minute={2}'.format(tps1m, tps5m, tps15m)

    if (args.critical is not None and tps15m < args.critical):
        status = 2
    elif (args.warning is not None and tps15m < args.warning):
        status = 1
    else:
        status = 0

elif (args.list is True):
    userlist = subprocess.getoutput('{0} -H {1} -P {2} -p {3} -c "list"'.format(args.mcrcon,
                                                                            args.host,
                                                                            args.port,
                                                                            args.password))
    returnusercount = userlist.split(" ")[2]
    returnmaxcount = userlist.split(" ")[7]
    status = 0
    resultstring = '{0} users of {1} connected.|current_users={0}; max_users={1}'.format(returnusercount, returnmaxcount)

print(resultstring)
sys.exit(status)
