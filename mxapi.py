# ****************************************************************************
# * mxapi.py
# * Mobotix api sender
#
# This script sends http api comands to (multiple) mobotix camera's 
# usage:
# python mxapi.py [options] 
# use option -h or --help for instructions
#
# release info
# 1.0 first release 140520 Paul Merkx
# ****************************************************************************
import os
import requests
import sys
import argparse
import csv
import io

RELEASE = '1.0 - 14 may 2020'
TIMEOUT = 3   # requests timeout

        
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


# ***************************************************************
# *** Main program ***
# ***************************************************************
print('MxProgram ' + RELEASE + ' by (c) Simac Healthcare.')
print('Disclaimer: ')
print('USE THIS SOFTWARE AT YOUR OWN RISK')
print(' ')

# *** Read arguments passed on commandline
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--deviceIP", nargs=1, help="specify target device IP when programming a single camera")
parser.add_argument("-l", "--devicelist", nargs=1, help="specify target device list in CSV when programming multiple camera's")
parser.add_argument("-a", "--apicommand", nargs=1, help="specify api command to send to camera(s).")
parser.add_argument("-u", "--username", nargs=1, help="specify target device admin username")
parser.add_argument("-p", "--password", nargs=1, help="specify target device admin password")
parser.add_argument("-s", "--ssl", help="use SSL to communicate (HTTPS)", action="store_true")
parser.add_argument("-t", "--timeout", nargs=1, help="specify cUrl timeout in seconds (default = 60)")

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

if args.timeout:
    try:
        TIMEOUT = int(args.timeout[0])
    except:
        print("Unable to understand timeout value of " + args.timeout[0])
        print("Try an interger")
        sys.exit()
        
if args.deviceIP:
    if not validate_ip(args.deviceIP[0]):
        print("The device %s is not a valid IPv4 address!" % (args.deviceIP[0]))
        sys.exit()

if args.devicelist:
    if not os.path.exists(args.devicelist[0]):
        print("The devicelist '%s' does not exist in the current directory!" % (args.devicelist[0]))
        sys.exit()

if not args.apicommand:
    print("The program requires an apicommand parameter! (like '-a /control/rcontrol')")
    print("Look at https://community.mobotix.com/t/getting-started-with-the-http-api/52 for more info")
    print("or in the help of the camera: http://<ip_address_for_the_camera>/help/help at to bottom of the page")
    sys.exit()

if args.ssl:
    use_ssl = True
else:
    use_ssl = False
    
print('Starting')
print('Build devicelist...')

# Build devicelist from devicelist file or from single parameter
# devicelist is a list of lists
devicelist = []
if args.devicelist:
    csv.register_dialect('semicolons', delimiter=';')
    with open(args.devicelist[0], 'r') as f:
        reader = csv.reader(f, dialect='semicolons')
        for row in reader:
            devicelist.append(row)
else:
    devicelist.append(['IP'])
    devicelist.append([args.deviceIP[0]])
#devicelist[0] now contains the header

for devicenr in range(1, len(devicelist)):  #skip header
    #skip device if starts with comment
    if devicelist[devicenr][0][0] != '#':
        ipaddr = devicelist[devicenr][0]
        print('About to program device ' + ipaddr + ' ', end='')
        if use_ssl:
            proto = "https://"
        else:
            proto = "http://"
        try:
            r = requests.get(proto + ipaddr + args.apicommand[0], auth=(username, password), timeout=TIMEOUT, verify=False)
            r.raise_for_status()
            if r.status_code == 200:
                print('...OK')
        except requests.exceptions.HTTPError as errh:
            print ("... Fail. Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("... Fail. Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("... Fail. Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("... Fail. Something weird happened ",err)
print("Done.")