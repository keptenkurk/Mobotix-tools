# ****************************************************************************
# * mxbackup.py
# * Mobotix camera configuration backup utility
#
# This script saves configuration files from (multiple) mobotix camera's
# through the Mobotix API
# See http://developer.mobotix.com/paks/help_cgi-remoteconfig.html for details
# usage:
# python mxbackup.py [options]
# use option -h or --help for instructions
# See https://github.com/keptenkurk/mxpgm/blob/master/README.md for
# instructions
#
# release info
# 1.0 first release 29/8/17 Paul Merkx
# 1.1 added SSL support and verbose switch, moved to Python3
# 1.2 -skip version
# 1.3 Change to using requests instead of pycurl
# ****************************************************************************
import os
import requests
from http import HTTPStatus
import sys
import argparse
import csv
import io
import datetime

RELEASE = '1.3 - 1-6-2020'
TMPCONFIG = 'config.tmp'
TIMEOUT = 10  # requests timeout (overwriteable by -t option)
# Ignore the warning that SSL CA will not be checked
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.
                                           exceptions.InsecureRequestWarning)


def filewritable(filename):
    try:
        f = open(filename, 'w')
        f.close()
    except IOError:
        print('Unable to write to ' + filename +
              '. It might be open in another application.')
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


def transfer(ipaddr, use_ssl, username, password, commandfile):
    # transfers commandfile to camera
    if use_ssl:
        url = 'https://' + ipaddr + '/admin/remoteconfig'
    else:
        url = 'http://' + ipaddr + '/admin/remoteconfig'
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


# ***************************************************************
# *** Main program ***
# ***************************************************************
print('MxBackup ' + RELEASE + ' by (c) Simac Healthcare.')
print('Saves entire configuration of multiple Mobotix camera\'s to \
      local disk.')
print('Disclaimer: ')
print('USE THIS SOFTWARE AT YOUR OWN RISK')
print(' ')

# *** Read arguments passed on commandline
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--deviceIP", nargs=1, help="\
                    specify target device IP when reading a single camera")
parser.add_argument("-l", "--devicelist", nargs=1, help="\
            specify target device list in CSV when reading multiple camera's")
parser.add_argument("-u", "--username", nargs=1, help="\
                    specify target device admin username")
parser.add_argument("-p", "--password", nargs=1, help="\
                    specify target device admin password")
parser.add_argument("-s", "--ssl", help="\
                    use SSL to communicate (HTTPS)", action="store_true")

args = parser.parse_args()

# *** Check validity of the arguments
if (args.deviceIP is None and args.devicelist is None) or \
   (args.deviceIP and args.devicelist):
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

if args.deviceIP:
    if not validate_ip(args.deviceIP[0]):
        print("Warning: The device %s is not a valid IPv4 address!"
              % (args.deviceIP[0]))
        print("Continuing using %s as devicename."
              % (args.deviceIP[0]))

if args.devicelist:
    if not os.path.exists(args.devicelist[0]):
        print("The devicelist '%s' does not exist in the current directory!"
              % (args.devicelist[0]))
        sys.exit()

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
    print('Found device ' + args.deviceIP[0])
    devicelist.append(['IP'])
    devicelist.append([args.deviceIP[0]])

for devicenr in range(1, len(devicelist)):
    # skip device if starts with comment
    if devicelist[devicenr][0][0] != '#':
        # build API commandfile to read the config
        if filewritable(TMPCONFIG):
            outfile = open(TMPCONFIG, 'w')
            outfile.write('\n')
            outfile.write('helo\n')
            outfile.write('view configfile\n')
            outfile.write('quit\n')
            outfile.write('\n')
            outfile.close()
            ipaddr = devicelist[devicenr][0]
            cfgfilename = ipaddr.replace(".", "-") + "_" + \
                datetime.datetime.now().strftime("%y%m%d-%H%M") + \
                ".cfg"
            if filewritable(cfgfilename):
                (result, received) = transfer(ipaddr, use_ssl,
                                              username, password, TMPCONFIG)
                if result:
                    print('Backup of ' + ipaddr + ' succeeded.')
                    outfile = open(cfgfilename, 'w')
                    outfile.write(received)
                    outfile.close()

                    # remove first 4 and last 3 lines
                    outfile = open(cfgfilename, 'r')
                    configfiledata = outfile.readlines()
                    outfile.close()

                    outfile = open(cfgfilename, 'w')
                    for line in range(4, len(configfiledata)-3):
                        outfile.write(configfiledata[line])
                    outfile.close()
                else:
                    print('ERROR: Reading of ' + ipaddr + ' failed.')
            os.remove(TMPCONFIG)
print("Done.")
