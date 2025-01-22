# ****************************************************************************
# * mxtract.py
# * Read a list of Mobotix cfg files and extract the camera dependant parameters
# * and save them in a CSV file. Field names can be used as label in a template config file
# * To be used with mxreplace.py which replaces 
#
# usage:
# python mxtract.py [options]
# use option -h or --help for instructions
# -o for outputfilename [smartsensor.csv]
# -s for sourcefilename(pattern) [current dir *.cfg]
#
#
# Pseudo
# get commandline params
# ask to overwrite smartsensor.cfg 
# for all camera_configs do:
#     read camera_config
#     extract known sensor specific data (ssd)
#     add to csv file
#     write(target_file)
#
# release info
# 1.0 first release 27-09-24 Paul Merkx
# ****************************************************************************
import os
import sys
import argparse
import time
import math
import csv


RELEASE = '1.0 - 27-9-2024'

#----string extraction helper-------
def extract_substring(input_string, start_char):
    start_index = input_string.find(start_char)
    if start_index == -1:
        return None  # Start character not found
    start_index += len(start_char)
    
    end_index = input_string.find(":", start_index)
    if end_index == -1:
        # the :  was not found, maybe eol?
        end_index = len(input_string)
    
    return input_string[start_index:end_index]


def replace_substring(input_string, start_char, end_char, replacement_string):
    start_index = input_string.find(start_char)
    if start_index == -1:
        return None  # Start character not found
    start_index += len(start_char)
    
    end_index = input_string.find(end_char, start_index)
    if end_index == -1:
       end_index = len(input_string)

    newstring = input_string[:start_index] + replacement_string + input_string[end_index:]
    #add newline in case parameter extends to end of line
    if end_index == len(input_string):
        newstring = newstring + '\n'
    return newstring


#---- build dictionairy with sensor specific config items
def getSSD(lines, cfgfile):
    ssd = {}
    ssd["file"] = cfgfile
    for line in lines:
#--Ethernet        
        sub = extract_substring(line,"HOSTNAME=")
        if sub!= None:
            ssd["HOSTNAME"] = sub.replace("\n", "") 
        sub = extract_substring(line,"IPADDR=")
        if sub!= None:
            ssd["IPADDR"] = sub.replace("\n", "")
        else:
            ssd["IPADDR"] = "DHCP"
        sub = extract_substring(line,"Camera IP: ")
        if sub!= None:
            ssd["DefaultIP"] = sub.replace("\n", "")
            
#-- actionhandler state
        sub = extract_substring(line,"ah1_arming=")
        if sub!= None:
            ssd["ah1_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah2_arming=")
        if sub!= None:
            ssd["ah2_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah3_arming=")
        if sub!= None:
            ssd["ah3_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah4_arming=")
        if sub!= None:
            ssd["ah4_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah5_arming=")
        if sub!= None:
            ssd["ah5_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah6_arming=")
        if sub!= None:
            ssd["ah6_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah7_arming=")
        if sub!= None:
            ssd["ah7_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah8_arming=")
        if sub!= None:
            ssd["ah8_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah9_arming=")
        if sub!= None:
            ssd["ah9_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah10_arming=")
        if sub!= None:
            ssd["ah10_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah11_arming=")
        if sub!= None:
            ssd["ah11_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah12_arming=")
        if sub!= None:
            ssd["ah12_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah13_arming=")
        if sub!= None:
            ssd["ah13_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah14_arming=")
        if sub!= None:
            ssd["ah14_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah15_arming=")
        if sub!= None:
            ssd["ah15_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah16_arming=")
        if sub!= None:
            ssd["ah16_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah17_arming=")
        if sub!= None:
            ssd["ah17_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah18_arming=")
        if sub!= None:
            ssd["ah18_arming"] = sub.replace("\n", "")
        sub = extract_substring(line,"ah19_arming=")
        if sub!= None:
            ssd["ah19_arming"] = sub.replace("\n", "")        
        sub = extract_substring(line,"ah20_arming=")
        if sub!= None:
            ssd["ah20_arming"] = sub.replace("\n", "") 
#-- audio state 
        sub = extract_substring(line,"MICRO=")
        if sub!= None:
            ssd["MICRO"] = sub.replace("\n", "")
            sub = extract_substring(line,"SPEAKER=")
        if sub!= None:
            ssd["SPEAKER"] = sub.replace("\n", "")
        sub = extract_substring(line,"SPEAKERLEVEL=")
        if sub!= None:
            ssd["SPEAKERLEVEL"] = sub.replace("\n", "")

#-- VOIP state and config 
        sub = extract_substring(line,"VOIPVOIP=")
        if sub!= None:
            ssd["VOIPVOIP"] = sub.replace("\n", "")          
        sub = extract_substring(line,":userid=")
        if sub!= None:
            ssd["userid"] = sub.replace("\n", "")
        sub = extract_substring(line,":authid=")
        if sub!= None:
            ssd["authid"] = sub.replace("\n", "")
        sub = extract_substring(line,"authpwd=")
        if sub!= None:
            ssd["authpwd"] = sub.replace("\n", "") 

#--- Events state and config
#--- Events state and config
# -badkamer VM3(ima)
# -Betreed kamer VM4 (ima)
# -Beweging VM5 (ima)
# -Geluid MI (env)
# -Logo aan: Logo_On (msg)
# -Logo uit: Loggo_Off (msg)
# Onrust: Bell5 (met)
# Te lang in badkamer: Bell3 (met)
# Te lnag uit bed: Bell2 (met)
# Te lang uit kamer: Bell4 (met)
# -Uit Bed: VM2 (ima)
# -Verlaat kamer: VM1 (ima)
# -Virtuele ronde: Virtuele_Ronde (msg)
        if "motion_area=" in line:
            sub = extract_substring(line, "motion_area=")
            if sub!= None:
                ssd["motion_area"] = sub.replace("\n", "")
 
        if "ima=VM1:" in line:
            sub = extract_substring(line,":activity_area=")
            if sub!= None:
                ssd["activity_area_VM1"] = sub.replace("\n", "")
            if "_profilestate=i" in line:
                ssd["profilestate_VM1"] = "inactive"
            else:
                ssd["profilestate_VM1"] = "active"               
            sub = extract_substring(line,"activity_directions=")
            if sub!= None:
                ssd["activity_directions_VM1"] = sub.replace("\n", "")
            sub = extract_substring(line,"vm_list=")
            if sub!= None:
                ssd["vm_list_VM1"] = sub.replace("\n", "")

        if "ima=VM2:" in line:
            sub = extract_substring(line,":activity_area=")
            if sub!= None:
                ssd["activity_area_VM2"] = sub.replace("\n", "")
            if "_profilestate=i" in line:
                ssd["profilestate_VM2"] = "inactive"
            else:
                ssd["profilestate_VM2"] = "active"               
            sub = extract_substring(line,"activity_directions=")
            if sub!= None:
                ssd["activity_directions_VM2"] = sub.replace("\n", "")
            sub = extract_substring(line,"vm_list=")
            if sub!= None:
                ssd["vm_list_VM2"] = sub.replace("\n", "")

        if "ima=VM3:" in line:
            sub = extract_substring(line,":activity_area=")
            if sub!= None:
                ssd["activity_area_VM3"] = sub.replace("\n", "")
            if "_profilestate=i" in line:
                ssd["profilestate_VM3"] = "inactive"
            else:
                ssd["profilestate_VM3"] = "active"               
            sub = extract_substring(line,"activity_directions=")
            if sub!= None:
                ssd["activity_directions_VM3"] = sub.replace("\n", "")
            sub = extract_substring(line,"vm_list=")
            if sub!= None:
                ssd["vm_list_VM3"] = sub.replace("\n", "")
                
        if "ima=VM4:" in line:
            sub = extract_substring(line,":activity_area=")
            if sub!= None:
                ssd["activity_area_VM4"] = sub.replace("\n", "")
            if "_profilestate=i" in line:
                ssd["profilestate_VM4"] = "inactive"
            else:
                ssd["profilestate_VM4"] = "active"               
            sub = extract_substring(line,"activity_directions=")
            if sub!= None:
                ssd["activity_directions_VM4"] = sub.replace("\n", "")
            sub = extract_substring(line,"vm_list=")
            if sub!= None:
                ssd["vm_list_VM4"] = sub.replace("\n", "")
                
        if "ima=VM5:" in line:
            sub = extract_substring(line,":activity_area=")
            if sub!= None:
                ssd["activity_area_VM5"] = sub.replace("\n", "")
            if "_profilestate=i" in line:
                ssd["profilestate_VM5"] = "inactive"
            else:
                ssd["profilestate_VM5"] = "active"               
            sub = extract_substring(line,"activity_directions=")
            if sub!= None:
                ssd["activity_directions_VM5"] = sub.replace("\n", "")
            sub = extract_substring(line,"vm_list=")
            if sub!= None:
                ssd["vm_list_VM5"] = sub.replace("\n", "")
                
        if "msg=Virtuele_Ronde:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Virtuele_Ronde"] = "inactive"
            else:
                ssd["profilestate_Virtuele_Ronde"] = "active"               

        if "msg=Virtuele_Ronde:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Virtuele_Ronde"] = "inactive"
            else:
                ssd["profilestate_Virtuele_Ronde"] = "active" 

        if "env=MI:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_MI"] = "inactive"
            else:
                ssd["profilestate_MI"] = "active"               
            sub = extract_substring(line,"mi_lvl=")
            if sub!= None:
                ssd["MI_lvl"] = sub.replace("\n", "")

        if "msg=Logo_On:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Logo_On"] = "inactive"
            else:
                ssd["profilestate_Logo_On"] = "active"

        if "msg=Logo_Off:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Logo_Off"] = "inactive"
            else:
                ssd["profilestate_Logo_Off"] = "active"

        if "msg=Logo_On:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Logo_On"] = "inactive"
            else:
                ssd["profilestate_Logo_On"] = "active"

        if "met=Bell1:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Bell1"] = "inactive"
            else:
                ssd["profilestate_Bell1"] = "active"

        if "met=Bell2:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Bell2"] = "inactive"
            else:
                ssd["profilestate_Bell2"] = "active"

        if "met=Bell3:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Bell3"] = "inactive"
            else:
                ssd["profilestate_Bell3"] = "active"
                
        if "met=Bell4:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Bell4"] = "inactive"
            else:
                ssd["profilestate_Bell4"] = "active"

        if "met=Bell5:" in line:
            if "_profilestate=i" in line:
                ssd["profilestate_Bell5"] = "inactive"
            else:
                ssd["profilestate_Bell5"] = "active"

    return ssd
            

def ExtractFile(cfgfile):
# Changes all sections of templatefile with data from readfile
    try:
        with open(cfgfile, 'r') as infile:
            cfglines = []
            for line in infile:
                cfglines.append(line)
            infile.close()
    except IOError:
        print("FATAL: Unable to read", cfgfile)
        sys.exit()
    
 # --- Get Sensor Specific Details
    ssd = getSSD(cfglines, cfgfile)

    return ssd

    
# ***************************************************************
# *** Main program ***
# ***************************************************************
start = time.time()

print('mxtract ' + RELEASE + ' by (c) Simac Healthcare.')
print('Disclaimer: ')
print('USE THIS SOFTWARE AT YOUR OWN RISK')
print(' ')

# *** Read arguments passed on commandline
parser = argparse.ArgumentParser()

parser.add_argument("-e", "--extension", nargs=1, help="\
                    specify source extension (default .cfg)")

args = parser.parse_args()

# *** Check validity of the arguments
    
if (args.extension) is None:
    print("Source files extension .cfg is assumed")
    source_ext = ".cfg"
else:
    print("Only processing ", args.extension[0], " files")
    source_ext = args.extension[0]

print('Start extracting device dependant data from Mobotix config files ')

nr_of_files = 0
all_ssd = []
      
#Extract data from all files in the directory with matching extension      
files = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
for f in files:
    # add pathname to file
    f = os.path.join(os.getcwd(), f)
    # check proper extension
    if f.endswith(source_ext):
        print("Extracting: ", f)
        all_ssd.append(ExtractFile(f))
        nr_of_files += 1
print("")

# Write Sensor Specific Data to CSV if any data found
if all_ssd:
    with open("smartsensor.csv", mode='w', newline='') as file:
        # Get the column names from the whole dictionary

        fieldnames = list({key for row in all_ssd for key in row.keys()})
        
        # Create a writer object
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header (column names)
        writer.writeheader()    
        # Write the data (rows)
        writer.writerows(all_ssd)
        print("CSV file smartsensor.csv created successfully!")

else:
    print("No Sensor Specific Data found to be saved.")

print("")
end = time.time()
exectime = round(1000*(end-start))
print("Extracted ", nr_of_files, " files in ", exectime, " milliseconds.")