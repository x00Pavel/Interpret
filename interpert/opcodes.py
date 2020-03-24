#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
 __author__  =  "Pavel Yadlouski (xyadlo00)"
 __project__ =  "Interpret for IPPcode20 language"
 __brief__   =  "Functions for all valid operation codes"
 __file__    =  "interpret/opcodes.py"
 __date__    =  "03.2020"
"""
import xml.etree.ElementTree as ET
import interpert.other_functions as fnc
import interpert.errors as err
import interpert.frames as fr

import pprint as pp
import sys
import re

# Don't have arguments

def create_frame_fnc(*args):
    fnc.frames['TF'] = fr.TemporaryFrame()


# Don't have arguments
def push_frame_fnc(*args):
    if fnc.frames['LF'] is None:
        fnc.frames['LF'] = fr.LocalFrame()
    if fnc.frames['TF'] is None:
        raise err.Err_55(frame='TF')
    fnc.frames['LF'].create_local_frame(fnc.frames['TF'].get_frame())
    fnc.frames['TF'].remove()
    fnc.frames['TF'] = None


# Don't have arguments
def pop_frame_fnc(*args):
    if fnc.frames['LF'] is None:
        raise err.Err_55(frame='LF')
    # if fnc.frames['TF'] is None:
    #     raise err.Err_55(frame='TF')
    # fnc.frame['TF']
    frame = fnc.frames['LF'].get_frame()
    fnc.frames['TF'] = fr.TemporaryFrame()
    fnc.frames['TF'].set_frame(frame)
    fnc.frames['LF'].remove_frame()

# TODO
def call_fnc(params: ET.Element):
    label = fnc.check_params(params, 1, 'CALL')

    if label not in fnc.list_labels.keys():
        raise err.Err_52(f"Label {label} is not specified yet.\n")


# Don't have arguments
def return_fnc(params: ET.Element):
    pass


def pushs_fnc(params: ET.Element):
    fnc.check_params(params, 1, 'PUSHS')
    # frame, item, index = fnc.get_item_from_frame(params[0].text)
    src_type = params[0].attrib['type']
    src_val = params[0].text
    fnc.stack.push({'value': src_val, 'type': src_type})


def pops_fnc(params: ET.Element):
    fnc.check_params(params, 1, 'POPS')
    frame, (item, index) = fnc.get_item_from_frame(params[0].text)
    val_to_insert = fnc.stack.pop()
    item['type'] = val_to_insert['type']
    item['value'] = val_to_insert['value']
    fnc.set_value_in_frame(frame, item, index)


def less_fnc(params: ET.Element):
    destination, first, second = fnc.check_params(params, 3, 'LT')
    first_type = fnc.get_type(first)
    second_type = fnc.get_type(second)

    if first_type != second_type or first_type == 'nil' or second_type == 'nil':
        raise err.Err_53(None, fnc='LT',
                         req_type=first_type, src_type=second_type)

    first_val = fnc.return_value(first, first_type, 'LT')
    second_val = fnc.return_value(second, second_type, 'LT')

    result = None
    if first_type == 'int':
        result = int(first_val) < int(second_val)
    elif first_type == 'string':
        result = len(first_val) < len(second_val)
    elif first_type == 'bool':
        if first_val == 'true' and second_val != 'true':
            result = 'false'
        elif first_val != 'true' and second_val == 'true':
            result = 'true'
        elif first_val != 'true' and second_val != 'true' or \
                first_val == 'true' and second_val == 'true':
            result = 'false'

    fnc.set_n_insert_val_type(destination, 'bool', result)


def greater_fnc(params: ET.Element):
    destination, first, second = fnc.check_params(params, 3, 'GT')
    first_type = fnc.get_type(first)
    second_type = fnc.get_type(second)

    if first_type != second_type or first_type == 'nil' or second_type == 'nil':
        raise err.Err_53(None, fnc='GT',
                         req_type=first_type, src_type=second_type)

    first_val = fnc.return_value(first, first_type, 'GT')
    second_val = fnc.return_value(second, second_type, 'GT')

    result = None
    if first_type == 'int':
        result = int(first_val) > int(second_val)
    elif first_type == 'string':
        result = len(first_val) > len(second_val)
    elif first_type == 'bool':
        if first_val == 'true' and second_val == 'false':
            result = 'true'
        elif first_val == 'false' and second_val == 'true':
            result = 'false'
        elif first_val != 'true' and second_val != 'true' or \
                first_val == 'true' and second_val == 'true':
            result = 'false'

    fnc.set_n_insert_val_type(destination, 'bool', result)


def equal_fnc(params: ET.Element):
    destination, first, second = fnc.check_params(params, 3, 'EQ')
    first_type = fnc.get_type(first)
    second_type = fnc.get_type(second)

    result = None
    if first_type is None or second_type is None:
        raise err.Err_56
    
    if first_type == 'nil':
        if second_type == 'nil':
            result = 'true'
        else:
            result = 'false'
    elif second_type == 'nil':
        if first_type == 'nil':
            result = 'true'
        else:
            result = 'false'
    elif first_type == second_type:
        first_val = fnc.return_value(first, first_type, 'EQ')
        second_val = fnc.return_value(second, second_type, 'EQ')

        if first_type == 'int':
            if int(first_val) == int(second_val):
                result = 'true'
            else:
                result = 'false'
        elif first_type == 'string':
            # print(second_val)
            first_val = fnc.convert_str(str(first_val))
            second_val = fnc.convert_str(str(second_val))
            if first_val == second_val:
                result = 'true'
            else:
                result = 'false'
        elif first_type == 'bool':
            if first_val != 'true' and second_val != 'true' or \
                    first_val == 'true' and second_val == 'true':
                result = 'true'
            else:
                result = 'false'
        else:
            raise err.Err_53(None, fnc='EQ',
                             req_type=first_type, src_type=second_type)
    else:
        raise err.Err_53(msg="Type in function 'EQ' can't be compared:"\
            f"{first_type} - {second_type}.\n")
    fnc.set_n_insert_val_type(destination.text, 'bool', result.lower())


def and_fnc(params: ET.Element):
    destination, first, second = fnc.check_params(params, 3, 'AND')
    first = fnc.return_value(first, 'bool', 'AND')
    second = fnc.return_value(second, 'bool', 'AND')
    if (first == 'true' and second == 'true'):
        fnc.set_n_insert_val_type(
            destination.text, 'bool', 'true')
    elif first == 'false' and second == 'false':
        fnc.set_n_insert_val_type(
            destination.text, 'bool', 'false')
    elif (first == 'true' and second == 'false') or \
            (first == 'false' and second == 'true'):
        fnc.set_n_insert_val_type(
            destination.text, 'bool', 'false')
    else:
        raise fnc.ERROR_32


def or_fnc(params: ET.Element):
    destination, first, second = fnc.check_params(params, 3, 'AND')
    try:
        first = fnc.return_value(first, 'bool', 'OR')
        second = fnc.return_value(second, 'bool', 'OR')
        fnc.set_n_insert_val_type(
            destination.text, 'bool', str(first or second))
    except:
        raise err.Err_32('Error in OR function.\n')


def not_fnc(params: ET.Element):
    destination, first = fnc.check_params(params, 2, 'NOT')
    try:
        first = fnc.return_value(first, 'bool', 'NOT')
        fnc.set_n_insert_val_type(destination.text, 'bool', str(not first))
    except:
        raise err.Err_32('Error in NOT function.\n')


def int_2_char_fnc(params: ET.Element):
    destination, source = fnc.check_params(params, 2, 'INT2CHAR')
    frame, (item, index) = fnc.get_item_from_frame(destination.text)
    src_type = ''
    src_val = ''
    if source.attrib['type'] == 'var':
        src_frame, (src_item, src_index) = fnc.get_item_from_frame(source.text)
        src_type = src_item['type']
        src_val = src_item['value']
    else:
        src_type = source.attrib['type']
        src_val = source.text

    if src_type != 'int':
        raise err.Err_53(None, fnc='INT2CHAR',
                         req_type='int', src_type=src_type)
    try:
        item['value'] = chr(int(src_val))
        item['type'] = 'string'
    except:
        raise err.Err_58(f"Value '{src_val}' can't be converted from 'int' type to "
                         "'string' type.\n")
    fnc.set_value_in_frame(frame, item, index)


def str_2_int_fnc(params: ET.Element):
    destination, string, index_of_char = fnc.check_params(params, 3, 'STRI2INT')
    frame, (item, index) = fnc.get_item_from_frame(destination.text)
    if string.attrib['type'] == 'var':
        str_frame, (str_item, str_index) = fnc.get_item_from_frame(string.text)
        if str_item['type'] != 'string':
            raise err.Err_53(None, fnc='STRI2INT', req_type='string',
                             src_type=str_item['type'])

        string = str_item['value']
    elif string.attrib['type'] == 'string':
        string = string.text
    else:
        raise err.Err_53(None, fnc='STRI2INT', req_type='string/var',
                         src_type=str_item['type'])

    if index_of_char.attrib['type'] == 'var':
        ind_frame, (ind_item, ind_index) = fnc.get_item_from_frame(
            index_of_char.text)
        if ind_item['type'] != 'int':
            raise err.Err_53(None, fnc='STRI2INT', req_type='int',
                             src_type=str_item['type'])

        try:
            index_of_char = int(ind_item['value'])
        except:
            raise err.Err_58(
                f"Value '{ind_item['value']}' can't be converted to 'int'.\n")
    elif index_of_char.attrib['type'] == 'int':
        try:
            index_of_char = int(index_of_char.text)
        except:
            raise err.Err_58(
                f"Value '{index_of_char.text}' can't be converted to 'int'.\n")
    if index_of_char < 0:
        raise err.Err_58(fnc='STRI2INT')
    try:
        char = string[index_of_char]
        item['value'] = ord(char)
        item['type'] = 'int'
        fnc.set_value_in_frame(frame, item, index)
    except:
        raise err.Err_58(fnc='STRI2INT')


def read_fnc(params: ET.Element, input_file):

    destination, type_ = fnc.check_params(params, 2, 'READ')
    if type_.attrib['type'] != 'type':
        raise err.Err_53(None, fnc='READ', req_type='type',
                         src_type=type_.attrib['type'])
    try:
        var = ''
        if input_file is None:
            var = input()
        else:
            var = input_file[0]

        frame, (item, index) = fnc.get_item_from_frame(destination.text)
        if type_.text == 'int':
            if not isinstance(var, int):
                var = 'nil'
        elif type_.text == 'string':
            if not isinstance(var, str):
                var = 'nil'
        elif type_.text == 'bool':
            if var.lower() == 'true':
                var = 'true'
            else:
                var = 'false'
        else:
            raise err.Err_58(fnc='READ')

        item['value'] = var
        item['type'] = type_.text if var != 'nil' else 'nil'
        fnc.set_value_in_frame(frame, item, index)
    except:
        raise err.Err_32(fnc='READ')


def strlen_fnc(params: ET.Element):
    destination, source = fnc.check_params(params, 2, 'STRLEN')
    try:
        value = fnc.return_value(source, 'string', 'STRLEN')
        fnc.set_n_insert_val_type(destination.text, 'int', len(value))
    except:
        raise err.Err_32(fnc='STRLEN')


def get_char_fnc(params: ET.Element):
    destination,( source, index )= fnc.check_params(params, 3, 'GETCHAR')

    string = fnc.return_value(source, 'string', 'GETCHAR')
    index = int(fnc.return_value(index, 'int', 'GETCHAR'))

    if index > len(string):
        raise err.Err_58(fnc='GETCHAR')
    else:
        fnc.set_n_insert_val_type(destination.text, 'string', string[index])


def set_char_fnc(params: ET.Element):
    source, index, char = fnc.check_params(params, 3, 'SETCHAR')

    index = int(fnc.return_value(index, 'int', 'SETCHAR'))
    char = fnc.return_value(char, 'string', 'SETCHAR')
    string = list(fnc.return_value(source, 'string', 'SETCHAR'))

    string[index] = char
    fnc.set_n_insert_val_type(source, 'string', "".join(string))


def type_fnc(params: ET.Element):
    destination, source = fnc.check_params(params, 2, 'TYPE')
    try:
        src_type = fnc.return_value(source, '', 'TYPE')
        fnc.set_n_insert_val_type(destination.text, 'type', src_type)
    except:
        raise err.Err_32(fnc='TYPE')


def jump_fnc(params: ET.Element):
    pass


def jump_if_eq_fnc(params: ET.Element):
    pass


def jump_if_neq_fnc(params: ET.Element):
    pass


def exit_fnc(params: ET.Element):
    pass


def dprint_fnc(params: ET.Element):
    pass


def break_fnc(params: ET.Element):
    pass


def def_var_fnc(params: ET.Element):
    # TODO split by @ and append to corresponding list of variables
    fnc.check_params(params, 1, 'DEFVAR')
    # if (len(params) != 1):
    #     raise err.Err_32("Wrong count of parameters while defining LABEL\n")

    try:
        if params[0].attrib['type'] != 'var':
            raise err.Err_53(None, fnc='DEFVAR', req_type='var',
                             src_type=params[0].attrib['type'])

        frame, var = (re.findall(r'^(GF|LF|TF)@(\w*)$', params[0].text))[0]
        if fnc.frames[frame] is None:
            raise err.Err_55(frame=frame)
        frame_list = fnc.frames[frame].get_frame()
        if var in [x['name'] for x in frame_list]:
            raise err.Err_52(var=var)
        fnc.frames[frame].set_var({'name': var, 'value': None, 'type': None})
    except:
        raise
        raise err.Err_32("Something wrong with parsing variables in DEFVAR\n")


def add_fnc(params: ET.Element):
    """
    Function for handling opcode ADD
    Arguments:
        * params: list of attributes of ElementTree Element
    """
    try:
        def_var, first_val, second_val = fnc.check_params(params, 3, 'ADD')
        frame, item, index, args = fnc.check_math(
            def_var, first_val, second_val)
        item['value'] = args[0] + args[1]
        item['type'] = 'int'
        fnc.set_value_in_frame(frame, item, index)
    except:
        raise




def concat_fnc(params: ET.Element):
    """
    Function for handling 'CONCAT' operation code
    Arguments:
        * params: list of attributes of ElementTree Element
    """
    try:
        def_var, first_val, second_val = fnc.check_params(params, 3, 'ADD')
        frame, item, index, args = fnc.check_math(
            def_var, first_val, second_val, 'string')
        str_1 = fnc.convert_str(args[0])
        str_2 = fnc.convert_str(args[1])
        item['type'] = 'string'
        item['value'] = str_1 + str_2
        fnc.set_value_in_frame(frame, item, index)
    except:
        raise


def write_fnc(params: ET.Element):
    arg = fnc.check_params(params, 1, 'WRITE')

    arg_type = arg.attrib['type']
    arg_val = arg.text
    to_print = ''
    if arg_type == 'var':
        frame, (item, index) = fnc.get_item_from_frame(arg_val)
        if item['type'] == 'nil':
            pass
        elif item['type'] == 'string':
            to_print = bytes(
                item['value'], "utf-8").decode("utf-8")
        else:
            to_print = item['value']
    elif arg_type == 'string':
        ar = re.findall(r'\\(\d{3})', arg_val)
        for a in ar:
            arg_val = re.sub(r'\\{}'.format(a), chr(int(a)), arg_val)
        to_print = arg_val
    elif arg_type == 'int' or arg_type == 'bool':
        to_print = arg_val
    sys.stdout.write(str(to_print))


def move_fnc(params):
    dest_var, value = fnc.check_params(params, 2, 'MOVE')

    if dest_var.attrib['type'] != 'var':
        raise err.Err_53(None, fnc='MOVE', req_type='var',
                         src_type=dest_var.attrib['type'])

    frame, (item, index) = fnc.get_item_from_frame(dest_var.text)
    if value.attrib['type'] == 'var':
        frame_src, item_src, index_src = fnc.get_item_from_frame(value.text)
        item['value'] = item_src['value']
        item['type'] = item_src['type']
    else:
        item['value'] = value.text
        item['type'] = value.attrib['type']

    fnc.set_value_in_frame(frame, item, index)


def label_fnc(params):
    label = fnc.check_params(params, 1, 'LABEL')
    if label.text not in fnc.list_labels:
        fnc.list_labels.append({label.text: params.attrib['order']})
    else:
        raise err.Err_52(var=label.text)


def sub_fnc(params):
    """
    Function for handling 'SUB' operation code
    Arguments:
        * params: list of attributes of ElementTree Element
    """
    try:
        def_var, first_val, second_val = fnc.check_params(params, 3, 'SUB')
        frame, item, index, args = fnc.check_math(
            def_var, first_val, second_val)
        item['value'] = args[0] + args[1]
        item['type'] = 'int'
        fnc.set_value_in_frame(frame, item, index)
    except:
        raise err.Err_32("Something wrong in TRY block of ADD function.\n")


def mul_fnc(params):
    """
    Function for handling opcode MUL
    Arguments:
        * params: list of attributes of ElementTree Element
    """
    try:
        def_var, first_val, second_val = fnc.check_params(params, 3, 'MUL')
        frame, item, index, args = fnc.check_math(
            def_var, first_val, second_val)
        item['value'] = args[0] * args[1]
        item['type'] = 'int'
        fnc.set_value_in_frame(frame, item, index)
    except:
        raise err.Err_32("Something wrong in TRY block of ADD function.\n")


def idiv_fnc(params):
    """
    Function for handling opcode IDIV
    Arguments:
        * params: list of attributes of ElementTree Element
    """
    try:
        def_var, first_val, second_val = fnc.check_params(params, 3, 'IDIV')
        frame, item, index, args = fnc.check_math(
            def_var, first_val, second_val)
        if 0 in args:
            raise err.Err_57("There is devision by zero.\n")
        item['value'] = args[0] + args[1]
        item['type'] = 'int'
        fnc.set_value_in_frame(frame, item, index)
    except:
        raise err.Err_32("Something wrong in TRY block of IDIV function.\n")
