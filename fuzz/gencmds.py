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

import defusedxml.ElementTree as ET
from xml.etree.ElementTree import Element
from collections import OrderedDict
import argparse
from argparse import RawTextHelpFormatter
import json
import os
import sys

from typing import List,Tuple

################################################################################
#  CONSTANTS & GLOBALS
################################################################################

debug0 = False
debug = False

# This flag is for commands that contain repeat arguments which we aren't
# handling yet
skipThisCommand = False

enumEntireList = []
cmdEntireList = []

################################################################################
#  FUNCTIONS
################################################################################
        
def gen_cmd_file(cmdfile):
    global enumEntireList
    global cmdEntireList

    # Get command xml file
    foundFile = False

    if not os.path.isfile(cmdfile):
        print('WARNING: Command XML file not found for: {}'.format(cmdfile))
        return -1
        
    
    # Parse xml into tree structure
    tree = ET.parse(cmdfile)

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


    cmds = root.find('command_definitions')

    cmdArray = []
    retCmdDict = {}
    for cmdroot in cmds:

        # Generate python class definition
        retCmdDict = write_cmd_class(cmdroot)
        if retCmdDict:
            cmdEntireList.append(retCmdDict)
        else:
            print("INFO: command {} not included in fuzz command dictionary ".format(cmdroot.attrib['stem']))

    if debug:
        print("\n\n\n GLOBAL cmdarray")
        for i in cmdEntireList:
            print(i)

    print('PROCESSED: {}'.format(cmdfile))

def write_cmd_class(cmdroot):
    global skipThisCommand
    cmdname = cmdroot.attrib['stem']
    newCmdKey = cmdname
    skipThisCommand = False
    
    # Name of Command
    outerDict = {}
    innerDict = {}
    # opcode
    # Add opcode field
    opcode = cmdroot.attrib['opcode']
    innerDict['opcode'] = opcode
    
    if debug0:
        print("cmdname is %s, opcode is %s"%(cmdname,opcode))

    # Add arguments
    reserved = []
    if cmdroot.find('arguments'):
        for field in cmdroot.find('arguments'):
            if debug0:
                print("cmdroot arguments %s"%field.tag)

            commandInfo = write_field(field, reserved)
            if not skipThisCommand:
                reserved.append(commandInfo)
            else:
                if debug0:
                    print("name SKIPPED is {} ".format(field.attrib['name']))

    if not skipThisCommand:
        innerDict['args'] = reserved
        outerDict[cmdname] = innerDict

        return outerDict
    else:
        skipThisCommand = False
        return None

def write_field(node, reserved=[]):
    global skipThisCommand

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
            print("this is float arg")
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
            print("this is integer arg")
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
        # This needs work. Ignoring the repeat args
        skipThisCommand = True
        return None
    else:
        bit_length = 0

    tmpDict['name'] = name
    tmpDict['type'] = type
    tmpDict['length'] = int(bit_length)
    tmpDict['range_min'] = int(min) if min else None
    tmpDict['range_max'] = int(max) if max else None

    return tmpDict


def write_enum_dicts(cmdroot):

    enumname = cmdroot.attrib['name']
    newEnumKey = enumname
    if debug0:
        print("enum name is %s"%enumname)

    # Add values
    enumVals = []
    newEnumDef = {}
    if cmdroot.find('values'):

        for field in cmdroot.find('values'):
            if debug0:
                print("enumroot arguments %s"%field.tag)

            enumVals.append(write_enum(field, enumname))

    else:
        print("ERROR: no enum values associated with {}".format(enumname))
        
    newEnumDef[newEnumKey] = enumVals
    return newEnumDef

def write_enum(node, enumName):

    #argument name
    enumValue = node.attrib['symbol']
    if debug0:
        print("this is in write_enum with enumname %s and enumvalue %s"%(enumName,enumValue))
    
    return enumValue


#def generate_commands(areas):
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
    # contain commands for a specified command xml file
    
    # This function will print the following to stdout:
    # INFO: informational message
    # CREATED: <new_file_path>
    # -- when a new file is created
    # WARNING: XML File not found
    # -- when the input XML file for a specified FSW area is not found
    # ERROR: error message
    # -- when the tool was not able to run successfully
    arealist = [areas]

    for i in arealist:
        gen_cmd_file(i)

    d1 = {}
    for i in enumEntireList:
        d1.update(i)
        
    d2 = {}
    for j in cmdEntireList:
        d2.update(j)
    
    return d1,d2

