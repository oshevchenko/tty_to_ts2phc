# tty2sock
Forward NMEA data from the serial interface to TCP socket.
This data could then be used by `ts2phc` service from LinuxPTP package.
To configure `ts2phc` use `ts2phc.nmea_remote_host`, `ts2phc.nmea_remote_port` options in `ts2phc` config file:
Similar functionality is provided by Linux `socat` tool:
```
socat TCP-LISTEN:4161,fork,reuseaddr FILE:/dev/ttyUSB1,b115200,raw

```

## Plug the GPS module to PC.
Serial device appears, for example `/dev/ttyUSB1`
## Run tty2sock
Check IP address:
```
oshevchenko@oshevchenko-pc:~/workspace/python_tutorial/tty_to_ts2phc$ ifconfig
...
enx00e04c70efa7: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.3.10  netmask 255.255.255.0  broadcast 192.168.3.255
        inet6 fe80::5f27:a89f:dc07:7d03  prefixlen 64  scopeid 0x20<link>
        ether 00:e0:4c:70:ef:a7  txqueuelen 1000  (Ethernet)
        RX packets 3  bytes 171 (171.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 78  bytes 14171 (14.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

```
Start the app:
```
python3 -m tty2sock /dev/ttyUSB1 192.168.3.10
```
Parsed NMEA data appears in the console log:
```
INFO:root:NMEA data {'GGA': {'Timestamp': '122220.000', 'Latitude': '4949.7546', 'Latitude Direction': 'N'....

```
## Start ts2phc on embedded board
Make sure to set the correct `ts2phc.nmea_remote_host`, `ts2phc.nmea_remote_port` options in `ts2phc` config file:
```
root@ok1046ac2v1:~# cat /etc/timemaster/ts2phc.conf
[global]
ts2phc.nmea_remote_host 192.168.3.10
ts2phc.nmea_remote_port 4161
logging_level 7
use_syslog 1
verbose 0
leapfile /usr/share/zoneinfo/leap-seconds-custom.list
step_threshold 0.1
[nmea]
ts2phc.master 1
[/dev/ptp0]
ts2phc.extts_correction -450
```
Restart the `ts2phc` service as:
```
systemctl restart ts2phc
```
Check the syslog output:
```
root@ok1046ac2v1:~# tail -f /var/log/syslog 
...
Feb  2 11:35:35 ok1046ac2v1 ts2phc: [66.502] /dev/ptp0 extts index 0 at 1675337772.999999560 corr -450 src 1675337765.439393500 diff 7999999110
Feb  2 11:35:35 ok1046ac2v1 ts2phc: [66.502] /dev/ptp0 ignoring invalid master time stamp
Feb  2 11:35:36 ok1046ac2v1 ts2phc: [66.973] nmea sentence: GPGGA,113536.000,4949.7531,N,02359.5972,E,1,18,0.6,409.5,M,36.5,M,,
Feb  2 11:35:36 ok1046ac2v1 ts2phc: [66.974] nmea sentence: GNGLL,4949.7531,N,02359.5972,E,113536.000,A,A
Feb  2 11:35:36 ok1046ac2v1 ts2phc: [66.975] nmea sentence: GNGSA,A,3,06,10,12,13,15,17,24,,,,,,1.1,0.6,0.9,1
...
```
