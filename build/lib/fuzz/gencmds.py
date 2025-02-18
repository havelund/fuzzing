#!/usr/bin/python3

"""
This module extracts the two dictionaries for:
(1) commands
(2) the enumeration types of their arguments.
The main function is `generate_commands`.
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import str
from past.builtins import basestring

from xml.etree import cElementTree as ET
from xml.etree.ElementTree import Element
from collections import OrderedDict
import json
import os
import sys

from typing import List,Tuple

################################################################################
#  CONSTANTS & GLOBALS
################################################################################

debug0 = False
debug = False

CMD_PATH = ['src/{}_mgr/{}_mgr_ai_cmd.xml',
            'src/{}_ctl/{}_ctl_ai_cmd.xml',
            'src/{}_svc/{}_svc_ai_cmd.xml',
            'src/{}_exe/{}_exe_ai_cmd.xml',
            'src/{}_ptm/{}_ptm_ai_cmd.xml']


enumEntireList = []
cmdEntireList = []

################################################################################
#  FUNCTIONS
################################################################################
        
def gen_cmd_file(fswpath, area):
    global enumEntireList
    global cmdEntireList

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
    
    # Parse xml into tree structure
    tree = ET.parse(cmd_path)

    root = tree.getroot()
    enumArray = []
        
    # Write Enum Structs
    enumStructs = root.find('enum_definitions')
    if enumStructs:
            
        for enumroot in enumStructs.findall('enum_table'):
            if debug0:
                print("in enumroot, %s"%enumroot.attrib['name'])
            
            # Generate python class definition
            retEnumDict = write_enum_dicts(enumroot)
            enumEntireList.append(retEnumDict)
            enumArray.append(retEnumDict)


    pkts = root.find('command_definitions')

    cmdArray = []
    retCmdDict = {}
    for pktroot in pkts:

        # Generate python class definition
        retCmdDict = write_cmd_packet_class(pktroot)
        if retCmdDict:
            cmdEntireList.append(retCmdDict)
        else:
            print("WARNING: command dict for {} returned None ".format(pktroot.attrib['stem']))

    if debug:
        print("\n\n\n GLOBAL cmdarray")
        for i in cmdEntireList:
            print(i)

    print('CREATED: {}'.format(area))

def write_cmd_packet_class(pktroot):
    cmdname = pktroot.attrib['stem']
#    print("cmdname is %s"%cmdname)

    skip_these_commands = ["DDM_DMP_EHA_PERIODIC","DDM_UPDATE_NUM_TSR","DDM_UPDATE_STR_TSR",
                           "DDM_DMP_EHA_HISTORY","GNC_IMU_WRITE_MEM","SEQ_VAR_CMD",
                           "SEQ_VAR_SEQ_ACTIVATE","SEQ_VAR_SEQ_LOAD","SEQ_VAR_SEQ_REACTIVATE",
                           "GNC_SRU_WRITE_MEMORY"]
    if cmdname in skip_these_commands:
        return
    newCmdKey = cmdname
    
    # Name of Command
    outerDict = {}
    innerDict = {}
    # opcode
    # Add opcode field
    opcode = pktroot.attrib['opcode']
    innerDict['opcode'] = opcode
    
    if debug0:
        print("pktname is %s, opcode is %s"%(cmdname,opcode))

    # Add arguments
    reserved = []
    if pktroot.find('arguments'):
        for field in pktroot.find('arguments'):
            if debug0:
                print("pktroot arguments %s"%field.tag)

            name = write_field(field, reserved)

            reserved.append(name)

    innerDict['args'] = reserved
    outerDict[cmdname] = innerDict

    return outerDict

def write_field(node, reserved=[]):

    #argument name
    name = node.attrib['name']
    tmpDict = {}
    min = None
    max = None
    found = False
    if node.tag == "var_string_arg":
        bit_length = node.attrib['max_bit_length']
        type = node.tag
        if debug0:
            print("this is var string arg {} {} {}".format(name,node.tag,bit_length))
    elif node.tag == "enum_arg":
        bit_length = node.attrib['bit_length']
        type = node.attrib['enum_name']
        if debug0:
            print("this is enum arg {} {} {}".format(name,node.tag, bit_length))
    elif node.tag == "unsigned_arg":
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
        if debug0:
            print("this is unsigned arg {} {} {}".format(name,node.tag,bit_length))
                
    elif node.tag == "float_arg":
        if debug0:
            print("TAC TAC this is float arg")
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
        if debug0:
            print("TAC TAC this is integer arg")
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
        min = None
        max = None
    else:
        bit_length = 0

    tmpDict['name'] = name
    tmpDict['type'] = type
    tmpDict['length'] = int(bit_length)
    tmpDict['range_min'] = int(min) if min else None
    tmpDict['range_max'] = int(max) if max else None
        
    return tmpDict


def write_enum_dicts(pktroot):

    enumname = pktroot.attrib['name']
    newEnumKey = enumname
    if debug0:
        print("enum name is %s"%enumname)

    # Add values
    enumVals = []
    newEnumDef = {}
    if pktroot.find('values'):

        for field in pktroot.find('values'):
            if debug0:
                print("enumroot arguments %s"%field.tag)

            enumVals.append(write_enum(field, enumname))

    else:
        print("ERROR: no enum values associated with {}".format(enumname))
        
    newEnumDef[newEnumKey] = enumVals
    return newEnumDef

def write_enum(node, enumName):

    #argument name
#    name = node.attrib['name']
    enumValue = node.attrib['symbol']
    if debug0:
        print("this is in write_enum with enumname %s and enumvalue %s"%(enumName,enumValue))
    
    return enumValue


def generate_commands(fsw_path: str, areas: List[str]) -> Tuple[dict, dict]:
    """
    Generates the enumeration type and command dictionary from the XML files.

    :param fsw_path: file path to the XML fsw directory.
    :param areas: the fsw areas to generate commands from.
    :return: the dictionaries representing resp. enumeration types and commands.
    """
    global enumEntireList
    global cmdEntireList

    # This function  generates python enum and command dictionaries that 
    # contain commands for a specified fsw area and the using the following xml 
    # definition files:
    # src/<fsw area>_mgr/<fsw area>_mgr_ai_cmd.xml',
    # src/<fsw area>_ctl/<fsw area>_ctl_ai_cmd.xml
    # src/<fsw area>_svc/<fsw area>_svc_ai_cmd.xml
    # src/<fsw area>_exe/<fsw area>_exe_ai_cmd.xml
    # src/<fsw area>_ptm/<fsw area>_ptm_ai_cmd.xml
    
    # fsw_path - path to the desired fsw version directory
    
    # This function will print the following to stdout:
    # INFO: informational message
    # CREATED: <new_file_path>
    # -- when a new file is created
    # WARNING: XML File not found
    # -- when the input XML file for a specified FSW area is not found
    # ERROR: error message
    # -- when the tool was not able to run successfully

    if not os.path.exists(fsw_path):
        print('ERROR: Path not found: {}'.format(fsw_path))
        exit(-1)

    for i in areas:
        gen_cmd_file(fsw_path, i)

    d1 = {}
    for i in enumEntireList:
        d1.update(i)
        
    d2 = {}
    for j in cmdEntireList:
        d2.update(j)
    
    return d1,d2


