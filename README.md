# MxPGM
Mobotix Remote configuration utility

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
processed within 20 seconds (a reboot takes about 12 seconds to process, the reboot itself
nearly 2 minutes).

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
Files can have any name. The devicelist file is a CSV file with ";" as a separator.

