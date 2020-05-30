# ****************************************************************************
# * mxpgm.py
# * Mobotix camera programmer
#
# This script programs (multiple) mobotix camera's through Mobotix API
# See http://developer.mobotix.com/paks/help_cgi-remoteconfig.html for details
# usage:
# python mxpgm.py [options] 
# use option -h or --help for instructions
# See https://github.com/keptenkurk/mxpgm/blob/master/README.md for instructions
#
# release info
# 1.0 first release 10/12/16 Paul Merkx
# 1.1 separate tools for backup and restor 29/8/17 Paul Merkx
# 1.2 added SSL support, verbose switch, timeout and moved to Python3 
# 1.3beta changed to the use of requests instead of pycurl
# ****************************************************************************
import os
import requests
import sys
import argparse
import csv
import io

RELEASE = '1.3beta - 30 may 2020'
TIMEOUT = 10  # requests timeout (overwriteable by -t option)
        
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

 
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

    
def transfer(ipaddr, use_ssl, username, password, commandfile):   
    #transfers commandfile to camera
    succeeded = False
    if use_ssl:
        url = 'https://' + ipaddr + '/admin/remoteconfig'
        verify=False
    else:
        url = 'http://' + ipaddr + '/admin/remoteconfig'
        verify=True
    try:
        with open(commandfile,'rb') as payload:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(url, auth=(username, password),
                       data=payload, verify=False, headers=headers,
                       timeout=TIMEOUT)
    except requests.ConnectionError:
        print('Unable to connect. ', end='')
        return succeeded, ''
    except requests.Timeout:
        print('Timeout. ', end='')
        return succeeded, ''     
    except requests.exceptions.RequestException as e:
        print('Uncaught error:', str(e), end='')
        return succeeded, ''     
    else:
        content = response.text            
        return True, content


# ***************************************************************
# *** Main program ***
# ***************************************************************
print('MxProgram ' + RELEASE + ' by (c) Simac Healthcare.')
print('Disclaimer: ')
print('USE THIS SOFTWARE AT YOUR OWN RISK')
print(' ')

# *** Read arguments passed on commandline
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verify", help="don't program camera yet but show resulting commandfile(s)", action="store_true")
parser.add_argument("-d", "--deviceIP", nargs=1, help="specify target device IP when programming a single camera")
parser.add_argument("-l", "--devicelist", nargs=1, help="specify target device list in CSV when programming multiple camera's")
parser.add_argument("-c", "--commandfile", nargs=1, help="specify commandfile to send to camera(s). See http://developer.mobotix.com/paks/help_cgi-remoteconfig.html")
parser.add_argument("-u", "--username", nargs=1, help="specify target device admin username")
parser.add_argument("-p", "--password", nargs=1, help="specify target device admin password")
parser.add_argument("-s", "--ssl", help="use SSL to communicate (HTTPS)", action="store_true")
parser.add_argument("-o", "--output", help="output device response to console", action="store_true")
parser.add_argument("-t", "--timeout", nargs=1, help="specify cUrl timeout in seconds (default = 10)")

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
        print("Warning: The device %s is not a valid IPv4 address!" % (args.deviceIP[0]))
        print("Assuming %s is the devicename instead." % (args.deviceIP[0]))

if args.devicelist:
    if not os.path.exists(args.devicelist[0]):
        print("The devicelist '%s' does not exist in the current directory!" % (args.devicelist[0]))
        sys.exit()

if args.commandfile:
    if not os.path.exists(args.commandfile[0]):
        print("The commandfile '%s' does not exist in the current directory!" % (args.commandfile[0]))
        sys.exit()
else:
    print("The program requires a commandfile parameter! (-c [file])")
    sys.exit()

if args.ssl:
    use_ssl = True
else:
    use_ssl = False
 
if args.output
    echo output = True
else:
    echo_output = False
    
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
#devicelist[0] now contains a list of labels we need to replace
#in the commandfile.

for devicenr in range(1, len(devicelist)):
    #skip device if starts with comment
    if devicelist[devicenr][0][0] != '#':
        #build replacement dictionary
        replacedict = {}
        for param in range(1, len(devicelist[devicenr])):
            replacedict['{' + devicelist[0][param] + '}'] = devicelist[devicenr][param]
        ipaddr = devicelist[devicenr][0]
        print('About to program device ' + ipaddr)
        infile = open(args.commandfile[0],'r')
        outfile = open('commands.tmp', 'w')
        outfile.write('\n') #commandfile starts with empty line is obligatory
        for line in infile:
            outfile.write(replace_all(line, replacedict))
        outfile.write('\n') #commandfile ending with empty line is obligatory
        infile.close()
        outfile.close()
        if args.verify:
            print('------------verify output------------')
            with open('commands.tmp', 'r') as outfile:
                print(outfile.read())
            print('-------------------------------------')
        else:
            (result, received) = transfer(ipaddr, use_ssl, username, password, 'commands.tmp')
            if result:
                print('Programming ' + ipaddr + ' succeeded.')
                if echo_output:
                    print(received)
            else:
                print('ERROR: Programming ' + ipaddr + ' failed.')
            print('')
print("Done.")