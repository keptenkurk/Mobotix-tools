# Mobotix Tools
The Mobotix-tools repository contains some utilities which might become handy
when configuring larger number of Mobotix camera's.
Currently it contains:
* mxbackup.py  -  Creates backups of a list of camera's just like the "Save current 
configuration to local computer" option on your camera but then performed automatically
on a list of camera's.
* mxrestore.py  -  Restores multiple backups made with mxbackup.py or manually with the 
"Save current configuration to local computer" option.
* mxpgm.py  -  Changes mobotix camera configurations on the fly according to the configuration
script supplied.
Instead of installing python3, Windows users can also use the executables from the /dist folder
in a DOS box.

DISCLAIMER: This software is built out of personal interest and not related to Mobotix AG 
in any way. You are free to use these tools for personal use. I will not be liable for any
damage, loss of data or other forms of unexpected behaviour. See MIT license for more details

# MxBackup
```
usage: python mxbackup.py [options]
Options:
-d  or  --deviceIP   = IPv4 address of the device to be backed up
-l  or  --devicelist = csv file with devices to be backed up. Must contains header line and 
IP address in first column
-u  or  --username   = Device username (default admin). All devices should use this username.
-p  or  --password   = Device password (default meinsm). All devices should use this password.
-s  or  --ssl        = Device will be contacted using HTTPS (certificate SA will not be checked
-v  or  --verbose    = Show cURL verbose
```
Currently different usernames/password for the devices in the list is not yet supported.

After supplying the correct arguments configuration backup files will be written named
IPaddress_datetime.cfg like: "192-168-1-24_170903-2214.cfg"

# MxRestore
```
usage: python mxrestore.py [options]
Options:
-d  or  --deviceIP   = IPv4 address of the device to be restored
-l  or  --devicelist = csv file with devices to be restored. Must contains header line and 
IP address in first column
-u  or  --username   = Device username (default admin). All devices should use this username.
-p  or  --password   = Device password (default meinsm). All devices should use this password.
Currently different usernames/password for the devices in the list is not yet supported.
-o  or  --override   = Override the warning when the Camera SW version of cfg file and camera
are different (this might cause seriouw trouble)
-r  or  --reboot     = Reboots the camera after the configuration has been restored
-s  or  --ssl        = Device will be contacted using HTTPS (certificate SA will not be checked
-v  or  --verbose    = Show cURL verbose
```
After supplying the correct arguments configuration backup files will be searched starting with 
an IPaddress as found in the provided list or device parameters like "192-168-1-24_*.cfg"
If a valid config file has bee found in the current directory the SW version number in the 
file is checked with the SW version of the camera. Should these not be the same the file will 
not be restored unless the -o or --override parameter is supplied.
The config in the file will be entirely restored, stored in flash and an update command is 
issued. A final reboot is optional an will be issued when supplying the -r or --reboot parameter.

# MxPgm
```
usage: python mxpgm.py [options]
Options:
-d  or  --deviceIP   = IPv4 address of the device to be restored
-l  or  --devicelist = csv file with devices to be restored. Must contains header line and 
IP address in first column
-u  or  --username   = Device username (default admin). All devices should use this username.
-p  or  --password   = Device password (default meinsm). All devices should use this password.
Currently different usernames/password for the devices in the list is not yet supported.
-c  or  --commandfile = filename of textfile containing commands to perform
are different (this might cause seriouw trouble)
-v  or  --verify     = Do not program but just show resulting merged commandfile
-f  or  --fileout    = filename of file to write output to. Just for checking later on
-s  or  --ssl        = Device will be contacted using HTTPS (certificate SA will not be checked
-o  or  --verbose    = Show cURL verbose
-t  ot  --timeout    = Override timeout (default 60 seconds)
```
Configuration changes could be easily made by backing up config files, changing them with a
text editor and restoring the result. Using MxPgm this is even easier.
Mobotix IP camera's come with an overwheling amount of configuration options. 
When configuring these camera's for larger projects it can be time saving when
configuration parameters can be pushed to a number of camera's at once.
Mobotix supports copying parts of the config to other camera's but often this 
overwrites parts you wouldn't like to be overwritten.
For instance: If you would like to enable the speaker on every camera you would 
need to copy the audio section which would overwrite the sip number which is 
unique to each camera.
So a more granular configuration tool would be useful.

Mobotix camera's support a Remote configuration API which enables to write 
configuration lines in the syntax found when viewing the camera's raw config.
This API is documented at http://developer.mobotix.com/paks/help_cgi-remoteconfig.html
MxPGM (short for Mobotix Programmer) utilizes this API.

The commands to be send to the camera first need to be saved in a configfile, like:
```
storeandreboot.conf:
  helo
  store
  reboot
  quit
```
Now we also need a list of device IP adresses to send these commands to like:
```
devicelist.csv
  IP
  192.168.1.100
  192.168.1.102
```

Say, these cam's have an admin account "john" with password "mysecret"
MxPGM can now be put to work with:
```
> python mxpgm.py -c storeandreboot.conf -l devicelist.csv -u john -p mysecret -v
```
The -v (verify) option tells mxpgm to just print out the commands without actually 
programming any camera. Then, leaving the -v out, the camera's can be programmed.
MxPGM will have a communication timeout of 5 seconds and will assume that a command is 
processed within 60 seconds (a reboot takes about 12 seconds to process, the reboot itself
nearly 2 minutes). If a longer timeout should be required the timeout can be overridden with
the -t option.

The devicelist could also contain parameters, unique to each camera, to be passed to the 
specific camera. Consider the example where we would like to configure the devicename of
each camera:
```
devicelist.csv
  IP;devicename
  192.168.1.100;Cam01
  192.168.1.102;Cam02
```
The configuration file can take the devicename parameter put between curly brackets
```
setdevicename.conf
  helo
  write params
  ethernet/HOSTNAME={devicename}
  store
  reboot
  quit
```
and issue MxPGM with
```
> python mxpgm.py -c setdevicename.conf -l devicelist.csv -u john -p mysecret -v
```
In these cases the -v option is valuable since we can verify the merging of the parameter
to avoid rubbish being send to the camera's.
Files can have any name. The devicelist file is a CSV file with ";" as a separator and 
starts with a header line.

When programming a single camera without parameters instead of a camera device list (the -l option)
a single IP can be passed with the -d option like:
```
> python mxpgm.py -c storeandreboot.conf -d 192.168.1.100 -u john -p mysecret -v
```
MxPgm supports writing the received output to file with the -f <filename> option.

# Hints & tips:
* The -d (device) parameter expects an IP address and will try to verify this.
Should your installation use hostnames instead use the -l (devicelist) option. These names or 
addresses won't be verified and can thus contain hostnames.
* Use the "write" option to replace an entire section when "write params" is not possible. This is 
usually the case when dealing with profiles which may have random generated profile ID's in it.
* If you still need to change a single line in a section with profiles, refer to the correct profile 
as described in the API documentation. Supply the profile name after the section: 
`<section name>/<profile name>/<parameter>=<value>`
example:
```
  helo
  write params
  events/ima_5a805a6b/ima=ima_5a805a6b:_profilename=VM2:ima_dead=5:ima_sens=vm:activity_level=33...etc
  store
  quit
```
* Be careful when programming camera's with a mix of software versions. A sample section taken from
a camera with a different firmware might not work on another firmware.
* Some configurations don't seem to end in a proper way and cause a timeout in the end. Although
after investigation the proper config seemed to be stored. 
* Using "append", "write" and "write params" in a single config file might cause trouble. 
Better write separate configs but be aware to use the right order when parts of these configs rely
on each other (like calling an IP Notify which needs to be programmed before).