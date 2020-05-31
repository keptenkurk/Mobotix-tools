# ****************************************************************************
# * mxrestore.py
# * Mobotix camera config restore utility
#
# This script restores configfiles to (multiple) mobotix camera's 
# through Mobotix API
# See http://developer.mobotix.com/paks/help_cgi-remoteconfig.html for details
# usage:
# python mxrstore.py [options] 
# use option -h or --help for instructions
# See https://github.com/keptenkurk/mxpgm/blob/master/README.md for
# instructions
#
# release info
# 1.0 first release 29/8/17 Paul Merkx
# 1.1 added -s (SSL) option and -v (verbose) option, removed bar and moved
# to Python3 
# 1.2 skipped version
# 1.3beta Changed PyCurl to requests
# ****************************************************************************
import os
import sys
import argparse
import csv
import datetime
import time
import glob
import math
import io

RELEASE = '1.3beta - 31 may 2020'
TMPCONFIG = 'config.tmp'
TMPCONFIG2 = 'config2.tmp'
TIMEOUT = 120 # saving config is generally slow
VERBOSE = 0   # show pycurl verbose


def filewritable(filename):
    try:
        f = open(filename, 'w')
        f.close()
    except IOError:
        print('Unable to write to ' + filename + '. It might be open \
              in another application.')
        return False
    os.remove(filename)
    return True


def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


def transfer(ipaddr, username, password, commandfile):
    # transfers commandfile to camera
    if use_ssl:
        url = 'https://' + ipaddr + '/admin/remoteconfig'
        verify = False
    else:
        url = 'http://' + ipaddr + '/admin/remoteconfig'
        verify = True
    try:
        with open(commandfile, 'rb') as payload:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(url, auth=(username, password),
                                     data=payload, verify=False,
                                     headers=headers, timeout=TIMEOUT)
    except requests.ConnectionError:
        print('Unable to connect. ', end='')
        return False, ''
    except requests.Timeout:
        print('Timeout. ', end='')
        return False, ''
    except requests.exceptions.RequestException as e:
        print('Uncaught error:', str(e), end='')
        return False, ''
    else:
        content = response.text
        if response:
            if (content.find('#read::') != 0):
                print('Are you sure this is Mobotix? ', end='')
                return False, ''
            else:
                return True, content
        else:
            print('HTTP response code: ',
                  HTTPStatus(response.status_code).phrase)
            return False, ''


def verify_version(cfgfileversion, deviceIP, username, password):
    #check if cfg to be restored has same SW version as device
    versionok = False
    result = False
    if filewritable(TMPCONFIG2):
        outfile = open(TMPCONFIG2, 'w')
        outfile.write('helo\n')
        outfile.write('view section timestamp\n')
        outfile.write('quit\n')
        outfile.close()
        (result, received) = transfer(ipaddr, username, password, TMPCONFIG2)
        if result:
            versionpos = received.find(b'VERSION=')
            datepos = received.find(b'DATE=')
            deviceversion = received[versionpos+8:datepos-1].decode("utf-8")
            # print('[' + deviceversion + '] - [' + cfgfileversion + ']')
            if deviceversion == cfgfileversion:
                versionok = True
            else:
                versionok = False
        os.remove(TMPCONFIG2)
    else:
        print('ERROR: Unable to write temporary file')
        sys.exit()
    return result, versionok


# ***************************************************************
# *** Main program ***
# ***************************************************************
print('MxRestore ' + RELEASE + ' by (c) Simac Healthcare.')
print('Restores entire configuration of multiple Mobotix camera\'s from disk.')
print('Disclaimer: ')
print('USE THIS SOFTWARE AT YOUR OWN RISK')
print(' ')

# *** Read arguments passed on commandline
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--deviceIP", nargs=1, help="specify target device IP when programming a single camera")
parser.add_argument("-l", "--devicelist", nargs=1, help="specify target device list in CSV when programming multiple camera's")
parser.add_argument("-u", "--username", nargs=1, help="specify target device admin username")
parser.add_argument("-p", "--password", nargs=1, help="specify target device admin password")
parser.add_argument("-o", "--override", help="write config even if SW versions are unequal", action="store_true")
parser.add_argument("-r", "--reboot", help="reboots camera after restoring", action="store_true")
parser.add_argument("-s", "--ssl", help="use SSL to communicate (HTTPS)", action="store_true")
parser.add_argument("-v", "--verbose", help="Show verbose output", action="store_true")

args = parser.parse_args()

# *** Check validity of the arguments
if (args.deviceIP is None and args.devicelist is None) or (args.deviceIP and args.devicelist):
    print("Either deviceIP or devicelist is required")
    sys.exit() 

if args.username is None:
    print("Default Admin account assumed")
    username = 'admin'
else:
    username = args.username[0]
 
if args.password is None:
    print("Default Admin password assumed")
    password = 'meinsm'
else:
    password = args.password[0]

if not args.deviceIP and not args.devicelist:
    print("No devices specified. Either specify a device (-d) or devicelist (-l)")
    sys.exit()
    
if args.deviceIP:
    if not validate_ip(args.deviceIP[0]):
        print("The device %s is not a valid IPv4 address!" % (args.deviceIP[0]))
        sys.exit()

if args.devicelist:
    if not os.path.exists(args.devicelist[0]):
        print("The devicelist '%s' does not exist in the current directory!" % (args.devicelist[0]))
        sys.exit()
        
if args.verbose:
    VERBOSE = 1

if args.ssl:
    use_ssl = True
else:
    use_ssl = False  
    
print('Starting')

# Build devicelist from devicelist file or from single parameter
# devicelist is a list of lists
devicelist = []
if args.devicelist:
    print('Build devicelist...')
    csv.register_dialect('semicolons', delimiter=';')
    with open(args.devicelist[0], 'r') as f:
        reader = csv.reader(f, dialect='semicolons')
        for row in reader:
            devicelist.append(row)
else:
    print('Found device '+ args.deviceIP[0])
    devicelist.append(['IP'])
    devicelist.append([args.deviceIP[0]])

for devicenr in range(1, len(devicelist)):
    #skip device if starts with comment
    if devicelist[devicenr][0][0] != '#':
        result = False
        ipaddr = devicelist[devicenr][0]
        cfgfilenamepattern = ipaddr.replace(".", "-") + "_*.cfg"
        list_of_files = glob.glob(cfgfilenamepattern)
        if len(list_of_files) > 0:
            latest_file = max(list_of_files, key=os.path.getctime)
            cfgfile = open(latest_file, 'r')
            cfgfileversion = ''
            for line in cfgfile.readlines():
                if line.find('#:MX-') == 0:
                    cfgfileversion = line[2:-1]
                    break
            (result, versionok) = verify_version(cfgfileversion, ipaddr, username, password)
            if result:
                if versionok:
                    print('SW version matches configfile version for device ' + ipaddr)
                else:
                    if args.override:
                        print('Non matching SW versions overridden by --override flag for device ' + ipaddr)
                if versionok or args.override:
                    # build API commandfile to read the config
                    if filewritable(TMPCONFIG):           
                        outfile = open(TMPCONFIG, 'w')
                        outfile.write('helo\n')
                        outfile.write('write\n')
                        cfgfile = open(latest_file, 'r')
                        for line in cfgfile:
                            outfile.write(line)
                        outfile.write('store\n')
                        outfile.write('update\n')
                        if args.reboot:
                            outfile.write('reboot\n')
                        outfile.write('quit\n')
                        outfile.close()
                        print('Restoring ' + ipaddr + '...')
                        (result, received) = transfer(ipaddr, username, password, TMPCONFIG)
                        if result:
                            print('Restoring of ' + latest_file + ' to ' + ipaddr + ' succeeded.')
                        else:
                            print('ERROR: Restoring of ' + ipaddr + ' failed.')
                        os.remove(TMPCONFIG)
                else:
                    print('SW version does not match configfile version for device ' + ipaddr)
                    print('Use -o or --override flag to ignore difference (but be aware of unexpected camera behaviour)')
            else:
                print('Unable to verify device SW version')
        else:
            print('No configfile found for device' + ipaddr)
        print('')
print("Done.")