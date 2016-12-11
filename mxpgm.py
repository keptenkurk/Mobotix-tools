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
# ****************************************************************************
import os
import pycurl
import sys
import argparse
import csv
from StringIO import StringIO

RELEASE = '1.0 - 3 dec 2016'

class FileReader:
    def __init__(self, fp):
        self.fp = fp
    def read_callback(self, size):
        return self.fp.read(size)

        
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
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

    
def transfer(ipaddr, username, password, commandfile):   
    #transfers commandfile to camera
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://' + ipaddr + '/admin/remoteconfig')
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 5)
    c.setopt(c.TIMEOUT, 30)
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
parser.add_argument("-f", "--fileout", nargs=1, help="specify output filename")
parser.add_argument("-g", "--getconfig", help="read config files from camera's in list", action="store_true")
parser.add_argument("-w", "--writeconfig", help="write configs found in current directory", action="store_true")
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

if args.commandfile:
    if not os.path.exists(args.commandfile[0]):
        print("The commandfile '%s' does not exist in the current directory!" % (args.commandfile[0]))
        sys.exit()
else:
    print("The program requires a commandfile parameter! (-c [file])")
    sys.exit()  
    
if args.getconfig: 
    print("This feature was not yet implemented")
    sys.exit()

if args.writeconfig: 
    print("This feature was not yet implemented")
    sys.exit()
    
if args.fileout:
    try:
        f = open(args.fileout[0], 'w')
        f.close()
    except IOError:
        print('Unable to write to outputfile. It might be opened in another application.')
        sys.exit()
    
print('Starting')
print('Build devicelist...')

# Build devicelist from devicelist file or from single parameter
# devicelist is a list of lists
devicelist = []
if args.devicelist:
    csv.register_dialect('semicolons', delimiter=';')
    with open(args.devicelist[0], 'rb') as f:
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
        for line in infile:
            outfile.write(replace_all(line, replacedict))
        infile.close()
        outfile.close()
        if args.verify:
            print('------------verify output------------')
            with open('commands.tmp', 'r') as outfile:
                print(outfile.read())
            print('-------------------------------------')
        else:
            (result, received) = transfer(ipaddr, username, password, 'commands.tmp')
            if result:
                print('Programming ' + ipaddr + ' succeeded.')
                if args.fileout:
                    try:
                        rxfile = open(args.fileout[0], 'w')
                        rxfile.write(received)
                        rxfile.close()
                    except IOError:
                        print('Error writing received results to file')
                        sys.exit()
            else:
                print('ERROR: Programming ' + ipaddr + ' failed.')
            print('')
print("Done.")