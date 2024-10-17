#!/usr/bin/python3
###############################################################################
# Copyright 2021, by the California Institute of Technology.
# ALL RIGHTS RESERVED. United States Government Sponsorship
# acknowledged. Any commercial use must be negotiated with the Office
# of Technology Transfer at the California Institute of Technology.
#
# Information included herein is controlled under the International
# Traffic in Arms Regulations ("ITAR") by the U.S. Department of State.
# Export or transfer of this information to a Foreign Person or foreign
# entity requires an export license issued by the U.S. State Department
# or an ITAR exemption prior to the export or transfer.
###############################################################################


from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import str
from past.builtins import basestring

from xml.etree import cElementTree as ET
from xml.etree.ElementTree import Element
from collections import OrderedDict
import json
import argparse
from argparse import RawTextHelpFormatter
import os
import sys
import re

################################################################################
#  CONSTANTS & GLOBALS
################################################################################

NA = 'None'


CMD_PATH = ['src/{}_mgr/{}_mgr_ai_cmd.xml',
            'src/{}_ctl/{}_ctl_ai_cmd.xml',
            'src/{}_svc/{}_svc_ai_cmd.xml',
            'src/{}_exe/{}_exe_ai_cmd.xml',
            'src/{}_ptm/{}_ptm_ai_cmd.xml']


ENUM_DEF = """
enumDict = {
"""
DICT_DEF = """
cmdDict = {
"""
DICT_NAME_ITEMS = "'\t%s':\{"
DICT_ITEMS = "\t\t'{}':'{}',\n"
DICT_ARGS_BEGIN = "\t\t'args': [\n"

DICT_ARGS_ITEM_NAME = "{'name':'{}', "
DICT_ARGS_ITEM_TYPE = "'type':'{}', "

DICT_ARGS_ITEM_LENGTH = "'length':{},\n"
DICT_ARGS_ITEM_RANGE_MIN = "'range_min':'{}'},\n"
DICT_ARGS_ITEM_RANGE_MAX = "'range_max':'{}'},\n"

DICT_ARGS_END = """
\t\t      ]
\t\t},
"""


global opcode_list


################################################################################
#  FUNCTIONS
################################################################################
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


        
def gen_cmd_file(fswpath, outdir, area):

    # Get command xml file
    foundFile = False
    for fswfmt in CMD_PATH:
        # Find xml cmd definition file
        cmd_path = os.path.join(fswpath, fswfmt.format(area, area))

        if os.path.isfile(cmd_path):
            print('INFO: Reading Command XML file: {}'.format(cmd_path))
            foundFile = True
            break

    if not foundFile:
        print('WARNING: Command XML file not found for: {}'.format(area))
        return -1
    
    # Reset list of cmd opcodes for this area
    global opcode_list
    opcode_list = []

    # Parse xml into tree structure
    tree = ET.parse(cmd_path)

    # Open an output file for packets
    pktpath = os.path.join(outdir, '{}Command.py'.format(area.capitalize()))
    
    with open(pktpath, 'w') as pktfile:

        root = tree.getroot()

        # Write Enum Structs
        enumStructs = root.find('enum_definitions')
        if enumStructs:
            pktfile.write(ENUM_DEF)
            
            for enumroot in enumStructs.findall('enum_table'):
#                print("in enumroot, %s"%enumroot.attrib['name'])
            
                # Generate python class definition
                write_enum_dicts(pktfile, enumroot)

            # Close class definition
            pktfile.write('}\n')
        
        # Write common dictionary header data
        pktfile.write(DICT_DEF)

        pkts = root.find('command_definitions')
#TAC        for pktroot in pkts.findall('fsw_command'):
#TAC            print("in pktroot, %s"%pktroot.attrib['stem'])
            
        for pktroot in pkts:

            # Generate python class definition
            write_cmd_packet_class(pktfile, pktroot)

        # Close class definition
        pktfile.write('}\n')

    print('CREATED: {}'.format(pktpath))


def write_enum_dicts(outfile,pktroot):
    global opcode_list
    enumname = pktroot.attrib['name']
#    print("enum name is %s"%enumname)

    # Name of Command
    outfile.write("\t'%s':[\n"%enumname)

    # Add values
    reserved = []
    if pktroot.find('values'):
#        outfile.write("'DICT_ARGS_BEGIN)
        for field in pktroot.find('values'):
#            print("enumroot arguments %s"%field.tag)

            write_enum(outfile, field, enumname)

#        outfile.write(DICT_ARGS_END)
        outfile.write("\t\t\t],\n")
    else:
        outfile.write('\t\t[],\n')

def write_cmd_packet_class(outfile, pktroot):
    global opcode_list
    cmdname = pktroot.attrib['stem']
#    print("cmdname is %s"%cmdname)

    skip_these_commands = ["DDM_DMP_EHA_PERIODIC","DDM_UPDATE_NUM_TSR","DDM_UPDATE_STR_TSR",
                           "DDM_DMP_EHA_HISTORY","GNC_IMU_WRITE_MEM","SEQ_VAR_CMD",
                           "SEQ_VAR_SEQ_ACTIVATE","SEQ_VAR_SEQ_LOAD","SEQ_VAR_SEQ_REACTIVATE",
                           "GNC_SRU_WRITE_MEMORY"]
    if cmdname in skip_these_commands:
        return
    
    # Name of Command
    outfile.write("\t'%s':{\n"%cmdname)

    # opcode
    # Add opcode field
    opcode = pktroot.attrib['opcode']
#    print("pktname is %s, opcode is %s"%(cmdname,opcode))
    if opcode in opcode_list:
        print("WARNING: Duplicate opcodes in {}: opcode={}".format(outfile.name, opcode))
    opcode_list.append(opcode)
    outfile.write(DICT_ITEMS.format('opcode', opcode))

    # # # # TAC I DON'T THINK I NEED THE crc16 field
    # Add arguments
    reserved = []
    if pktroot.find('arguments'):
        outfile.write(DICT_ARGS_BEGIN)
        for field in pktroot.find('arguments'):
#            print("pktroot arguments %s"%field.tag)

            name = write_field(outfile, field, reserved)
            reserved.append(name)

        outfile.write(DICT_ARGS_END)
    else:
        outfile.write('\t\t\'args\': []\n\t\t},\n')


def write_enum(outfile, node, enumName):

    #argument name
#    name = node.attrib['name']
    enumValue = node.attrib['symbol']
#    print("this is in write_enum with enumname %s and enumvalue %s"%(enumName,enumValue))
    
#    outfile.write("\t\t\t{'%s':["%(enumName))
#    for field in node:
    outfile.write("\t\t\t'%s',\n"%enumValue)

        
    return

def write_field(outfile, node, reserved=[]):

    #argument name
    name = node.attrib['name']

    min = "None"
    max = "None"
    found = False
    if node.tag == "var_string_arg":
#        print("this is var string arg")
        bit_length = node.attrib['max_bit_length']
        type = node.tag
#        print("this is var string arg {} {} {}".format(name,node.tag,bit_length))
    elif node.tag == "enum_arg":
        bit_length = node.attrib['bit_length']
        type = node.attrib['enum_name']
#        print("this is enum arg {} {} {}".format(name,node.tag, bit_length))
    elif node.tag == "unsigned_arg":
        bit_length = node.attrib['bit_length']
        type = node.tag
        for field in node:
#            print("this is unsigned arg, in field loop")
            if field.tag == 'range_of_values':
                for range in field:
                    min = range.attrib['min']
                    max = range.attrib['max']
                    found = True
                    break
            if found:
                break
#        print("this is unsigned arg {} {} {}".format(name,node.tag,bit_length))
                
    elif node.tag == "float_arg":
#        print("TAC TAC this is float arg")
        bit_length = node.attrib['bit_length']
        type = node.tag
        for field in node:
            if field.tag == 'range_of_values':
                for range in field:
                    min = range.attrib['min']
                    max = range.attrib['max']
                    found = True
                    break
            if found:
                break

    elif node.tag == "integer_arg":
#        print("TAC TAC this is integer arg")
        bit_length = node.attrib['bit_length']
        type = node.tag
        for field in node:
            if field.tag == 'range_of_values':
                for range in field:
                    min = range.attrib['min']
                    max = range.attrib['max']
                    found = True
                    break
            if found:
                break
    elif node.tag == "repeat_arg":
#        print("TAC TAC TAC This needs work. There are 11 of these. Maybe ignore these commands until we have everything else working.  this is repeat arg")
        bit_length = node.attrib['bit_length']
        type = node.tag
        min = "None"
        max = "None"
    else:
        bit_length = 0

    outfile.write("\t\t\t{'name':'%s','type':'%s','length':%s,'range_min':%s,'range_max':%s},\n"%(name,type,bit_length,min,max))
        
    return


def write_eha_dict_mapping(outfile, pktroot):
    dictname = pktroot.attrib['packet_name'].upper() + '_EHA_MAP'
    
    # Build dict mapping (EHA -> itlm field)
    ehadict = OrderedDict()
    for field in pktroot.find('fields'):
        if 'flight_channel_map' in field.attrib:
            channel = field.attrib['flight_channel_map']
            itlm_field = field.attrib['name']
            ehadict[channel] = itlm_field

    # Write nothing if empty
    if len(ehadict) == 0:
        return

    # Write dict definition
    outfile.write('\n{} = \\\n'.format(dictname))
    outfile.write(json.dumps(ehadict, indent=4) + '\n')


################################################################################
#  MAIN
################################################################################

desc = """This tool generates python enum and command dictionaries that 
contain commands for a specified fsw area and the using the following xml 
definition files:
            src/<fsw area>_mgr/<fsw area>_mgr_ai_cmd.xml',
            src/<fsw area>_ctl/<fsw area>_ctl_ai_cmd.xml
            src/<fsw area>_svc/<fsw area>_svc_ai_cmd.xml
            src/<fsw area>_exe/<fsw area>_exe_ai_cmd.xml
            src/<fsw area>_ptm/<fsw area>_ptm_ai_cmd.xml


A path to the desired fsw version directory is required.

The following output files will be generated for each fsw area:
    <fsw Area>Command.py

This tool will print the following to stdout:
    INFO: informational message
    CREATED: <new_file_path>
        -- when a new file is created
    WARNING: XML File not found
        -- when the input XML file for a specified FSW area is not found
    ERROR: error message
        -- when the tool was not able to run successfully
"""
parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
parser.add_argument('fswpath', type=str, help='root of desired eurcfsw repo')
parser.add_argument('-o', '--outdir', type=str, default='.',
    help='directory for output files (default: pwd)')
parser.add_argument('-i', '--fswArea', type=str, action='append', nargs='+', default=None,
    help='fsw area, requires at least one fsw area')

args = parser.parse_args()

if not args.fswArea:
    print('ERROR: No FSW Areas specified')
    exit(-1)

fswAreaArray = []
for i in args.fswArea:
    fswAreaArray.append(i[0])

if not os.path.exists(args.fswpath):
    print('ERROR: Path not found: {}'.format(args.fswpath))
    exit(-1)

if not os.path.exists(args.outdir):
    os.mkdir(args.outdir)
    print('INFO: Created output directory: {}'.format(args.outdir))


for i in fswAreaArray:
    gen_cmd_file(args.fswpath, args.outdir, i)

