# check_spigot_minecraft
A Nagios plugin for monitoring Spigot based Minecraft servers via RCON.

# Installation
Not much to note about installation other than this script does not directly handle RCON. You do have the option to specify an RCON client. In my case I used [mcrcon](https://github.com/Tiiffi/mcrcon.git), which is why I have it listed in the help section.

# Usage

```
usage: check_spigot_minecraft.py [-h] [-H HOST] -p PASSWORD [-P PORT] [-l LIST] [-m MCRCON] [-w WARNING] [-c CRITICAL] {tps} ...

positional arguments:
  {tps}                 sub-command help
    tps                 Monitor TPS and/or memory utilization

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  IP address of the Minecraft server
  -p PASSWORD, --password PASSWORD
                        rcon password for the Minecraft server
  -P PORT, --port PORT  rcon port for the Minecraft server
  -l LIST, --list LIST  List the number of players on the server
  -m MCRCON, --mcrcon MCRCON
                        Path to the mcrcon binary, including binary name.
  -w WARNING, --warning WARNING
                        Set the warning threshold
  -c CRITICAL, --critical CRITICAL
                        Set the critical threshold
```

```
usage: check_spigot_minecraft.py tps [-h] [-k {tps,memory}]

optional arguments:
  -h, --help            show this help message and exit
  -k {tps,memory}, --key {tps,memory}
                        Set the key metric. e.g. tps or memory
```

Host specifies the host that you want to check.

Password specifies the RCON password for the host.

Port specifies the port that RCON is listening on, default is 25575

List will list the number of users currently connected to the server.

Mcrcon will specify the location of the mcrcon binary

Warning and Critical will set thresholds for user count, TPS, or memory utilization. These are optional if you just want to track the usage. They will output in Nagios format, with performance data.

The tps positional argument lets you specify whetehr you want to check the TPS on the server, or the memory utilization.

# Things to Note
When monitoring TPS, Spigot Minecraft, and by proxy mcrcon, will return 1 minute, 5 minute, and 15 minute TPS values. In v1.0 of the script, all three of these metrics will be reported back, and tracked in the performance data, however the warning and critical thresholds only apply to the 15 minute TPS value. In the future I'd like to make an option to just specify which interval you'd like to monitor, but in the meantime if you'd like to change that, line 124 starts the check against the warning/critical thresholds. I do break out all three intervals into their own variables, so it can be changed pretty easily.

Also remember when monitoring TPS that a lower value is worse. Therefore your warning threshold should be a higher number than your critical threshold.
