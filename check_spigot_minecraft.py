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
parser.add_argument('-m',
                    '--metric',
                    required=False,
                    type=str,
                    choices=['list','tps','memory'],
                    help='The metric you would like to monitor')
parser.add_argument('-M',
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


args = parser.parse_args(sys.argv[1:])

resultstring = 'Nothing changed the result string'

def getdata(metric):
    try:
        tpsdata = subprocess.getoutput('{0} -H {1} -P {2} -p {3} -c "{4}"'.format(args.mcrcon,
                                                                                     args.host,
                                                                                     args.port,
                                                                                     args.password,
                                                                                     metric))
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit(2)

    return tpsdata


if (args.metric == 'memory'):
    #Using tps as the metric here, because memory and ticks per second are grabbed by the same command
    tpsdata = getdata('tps')

    returnmem = str(tpsdata).split(" ")[11]
    usedmem = int(returnmem.split('/')[0])
    maxmem = int(returnmem.split('/')[1])
    resultstring = 'Memory: {0} used of {1} max | used_mem={0}; max_mem={1}'.format(usedmem, maxmem)

    if (args.critical is not None and usedmem > args.critical):
        status = 2
    elif (args.warning is not None and usedmem > args.warning):
        status = 1
    else:
        status = 0


elif (args.metric == 'tps'):
    tpsdata = getdata('tps')

    if (args.critical is not None and args.warning is not None):
        if (args.warning < args.critical):
            resultstring = 'When alerting on TPS, lower is worse. Warning should be a higher number than critical.'
            status = 3
            
            print(resultstring)
            sys.exit(status)

    returntps = str(tpsdata).split("\n")[0]
    tps1m = returntps.split(' ')[6][0:(len(returntps.split(' ')[6]) - 1)]
    tps5m = returntps.split(' ')[7][0:(len(returntps.split(' ')[7]) - 1)]
    tps15m = returntps.split(' ')[8]

    if ('*' in tps1m):
        tps1m = tps1m.split('*')[1]

    if ('*' in tps5m):
        tps5m = tps5m.split('*')[1]

    if ('*' in tps15m):
        tps15m = tps15m.split('*')[1]

    resultstring = 'tps times were {0}, {1}, {2}|tps_1minute={0}; tps_5minute={1}; tps_15minute={2}'.format(tps1m, tps5m, tps15m)

    if (args.critical is not None and float(tps15m) < args.critical):
        status = 2
    elif (args.warning is not None and float(tps15m) < args.warning):
        status = 1
    else:
        status = 0

elif (args.metric == 'list'):
    tpsdata = getdata('list')
    returnusercount = str(tpsdata).split(" ")[2]
    returnmaxcount = str(tpsdata).split(" ")[7]
    status = 0
    resultstring = '{0} users of {1} connected.|current_users={0}; max_users={1}'.format(returnusercount, returnmaxcount)

print(resultstring)
sys.exit(status)
