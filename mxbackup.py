# ****************************************************************************
# * mxbackup.py
# * Mobotix camera configuration backup utility
#
# This script saves configuration files from (multiple) mobotix camera's through 
# the Mobotix API
# See http://developer.mobotix.com/paks/help_cgi-remoteconfig.html for details
# usage:
# python mxbackup.py [options] 
# use option -h or --help for instructions
# See https://github.com/keptenkurk/mxpgm/blob/master/README.md for instructions
#
# release info
# 1.0 first release 29/8/17 Paul Merkx
# ****************************************************************************
import os
import pycurl
import sys
import argparse
import csv
import datetime
from StringIO import StringIO

RELEASE = '1.0 - 3 dec 2016'
tmpconfig = 'config.tmp'
tmpbackup = 'backup.tmp'

class FileReader:
    def __init__(self, fp):
        self.fp = fp
    def read_callback(self, size):
        return self.fp.read(size)


def filewritable(filename):
    try:
        f = open(filename, 'w')
        f.close()
    except IOError:
        print('Unable to write to %s. It might be opened in another application. Skip operation.', filename)
        return False
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
    #transfers commandfile to camera
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://' + ipaddr + '/admin/remoteconfig')
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 5)
    # programming a full config, update and store takes quite some time
    c.setopt(c.TIMEOUT, 120)
    filesize = os.path.getsize(commandfile)
    f = open(commandfile, 'rb')
    c.setopt(c.FAILONERROR, True)
    c.setopt(pycurl.POSTFIELDSIZE, filesize)
    c.setopt(pycurl.READFUNCTION, FileReader(f).read_callback)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.setopt(pycurl.HTTPHEADER, ["application/x-www-form-urlencoded"])
    c.setopt(c.VERBOSE, 0)
    c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    c.setopt(pycurl.USERPWD, username + ':' + password)
    try:
        c.perform()
    except pycurl.error, error:
        errno, errstr = error
        print 'An error occurred: ', errstr
        return False, ''
    c.close()
    content = storage.getvalue()
    f.close()
    return True, content


# ***************************************************************
# *** Main program ***
# ***************************************************************
print('MxBackup ' + RELEASE + ' by (c) Simac Healthcare.')
print('Disclaimer: ')
print('USE THIS SOFTWARE AT YOUR OWN RISK')
print(' ')

# *** Read arguments passed on commandline
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verify", help="don't program camera yet but show resulting commandfile(s)", action="store_true")
parser.add_argument("-d", "--deviceIP", nargs=1, help="specify target device IP when programming a single camera")
parser.add_argument("-l", "--devicelist", nargs=1, help="specify target device list in CSV when programming multiple camera's")
parser.add_argument("-u", "--username", nargs=1, help="specify target device admin username")
parser.add_argument("-p", "--password", nargs=1, help="specify target device admin password")

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
    
if args.deviceIP:
    if not validate_ip(args.deviceIP[0]):
        print("The device %s is not a valid IPv4 address!" % (args.deviceIP[0]))
        sys.exit()

if args.devicelist:
    if not os.path.exists(args.devicelist[0]):
        print("The devicelist '%s' does not exist in the current directory!" % (args.devicelist[0]))
        sys.exit()
    
print('Starting')

# Build devicelist from devicelist file or from single parameter
# devicelist is a list of lists
devicelist = []
if args.devicelist:
    print('Build devicelist...')
    csv.register_dialect('semicolons', delimiter=';')
    with open(args.devicelist[0], 'rb') as f:
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
        # build API commandfile to read the config
        outfile = open(tmpconfig, 'w')
        outfile.write('helo\n')
        outfile.write('view configfile\n')
        outfile.write('quit\n')
        outfile.close()
        ipaddr = devicelist[devicenr][0]
        cfgfilename = ipaddr.replace(".", "-") + "_" + \
                      datetime.datetime.now().strftime("_%y%m%d-%H%M") + ".cfg"
        if filewritable(cfgfilename):
            (result, received) = transfer(ipaddr, username, password, tmpconfig)
            if result:
                print('Reading of ' + ipaddr + ' succeeded.')
                outfile = open(cfgfilename, 'w')
                outfile.write(received)
                outfile.seek(-24,2)
                outfile.truncate()
                outfile.close()
            else:
                print('ERROR: Reading of ' + ipaddr + ' failed.')
        print('')
print("Done.")