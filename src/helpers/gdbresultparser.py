# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2011  The ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
#
# This file is part of ricodebug.
#
# ricodebug is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further information see <http://syscdbg.hagenberg.servus.at/>.
"""Lexical parser for the gdb output

For futher information see the ply python module documentation.
"""


import ply.lex as lex
import ply.yacc as yacc
from .gdboutput import GdbOutput
import helpers.excep
import re
from .tools import unBackslashify
from PyQt4.QtCore import QDir

reserved = {
    "done": "DONE",
    "running": "RUNNING",
    "connected": "CONNECTED",
    "error": "ERROR",
    "exit": "EXIT",
    "stopped": "STOPPED",
    "thread-created": "THREAD_CREATED",
    "thread-group-created": "THREAD_GROUP_CREATED",
    "thread-group-added": "THREAD_GROUP_ADDED",
    "thread-group-started": "THREAD_GROUP_STARTED",
    "thread-exited": "THREAD_EXITED",
    "thread-group-exited": "THREAD_GROUP_EXITED",
    "thread-selected": "THREAD_SELECTED",
    "library-loaded": "LIBRARY_LOADED",
    "library-unloaded": "LIBRARY_UNLOADED",
    "breakpoint-modified": "BREAKPOINT_MODIFIED",
    "breakpoint-created": "BREAKPOINT_CREATED"
}

tokens = [
    "ASSIGN",
    "COMMA",
    "LBRACE",
    "RBRACE",
    "LBRACKET",
    "RBRACKET",
    "HAT",
    "STAR",
    "PLUS",
    "TILDE",
    "AT",
    "AMP",
    "C_STRING",
    "STRING",
] + list(reserved.values())

t_ASSIGN = r'='
t_COMMA = r','
t_LBRACE = r'{'
t_RBRACE = r'}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_HAT = r'\^'
t_STAR = r'\*'
t_PLUS = r'\+'
t_TILDE = r'~'
t_AT = r'@'
t_AMP = r'&'


def t_STRING(t):
    r'[\w\d_-]+'
    t.type = reserved.get(t.value, "STRING")
    return t


def t_C_STRING(t):
    r'".*?(?<!\\)"(?=(,|\}|\]|$))'
    t.value = unBackslashify(t.value)
    t.value = t.value[1:-1]  # strip the "
    return t


def t_error(t):
    raise TypeError("Unknown text '%s'" % (t.value,))


class Result:
    def __str__(self):
        return "RESULT(" + self.__dict__.__str__() + ")"


class Assignment:
    def __init__(self, dest, src):
        self.dest = dest
        self.src = src

    def __str__(self):
        return "ASSIGN(" + self.dest.__str__() + "," + self.src.__str__() + ")"


def p_result_record(p):
    '''result_record : result_class
                     | result_class COMMA result_list'''
    p[0] = GdbOutput()

    p[0].class_ = p[1]
    if len(p) == 4:
        for a in p[3]:
            setattr(p[0], a.dest, a.src)


def p_async_output(p):
    '''async_output : async_class
                    | async_class COMMA result_list'''
    p[0] = GdbOutput()
    p[0].class_ = p[1]

    if len(p) == 4:
        p[0].results = p[3]


def p_result_class(p):
    '''result_class : DONE
                    | RUNNING
                    | CONNECTED
                    | ERROR
                    | EXIT'''
    if p[1] == "done":
        p[0] = GdbOutput.DONE
    elif p[1] == "running":
        p[0] = GdbOutput.RUNNING
    elif p[1] == "connected":
        p[0] = GdbOutput.CONNECTED
    elif p[1] == "error":
        p[0] = GdbOutput.ERROR
    elif p[1] == "exit":
        p[0] = GdbOutput.EXIT


def p_async_class(p):
    '''async_class : STOPPED
                   | RUNNING
                   | THREAD_CREATED
                   | THREAD_GROUP_CREATED
                   | THREAD_GROUP_ADDED
                   | THREAD_GROUP_STARTED
                   | THREAD_EXITED
                   | THREAD_GROUP_EXITED
                   | THREAD_SELECTED
                   | LIBRARY_LOADED
                   | LIBRARY_UNLOADED
                   | BREAKPOINT_MODIFIED
                   | BREAKPOINT_CREATED'''
    if p[1] == "stopped":
        p[0] = GdbOutput.STOPPED
    elif p[1] == "running":
        p[0] = GdbOutput.RUNNING
    elif p[1] == "thread-created":
        p[0] = GdbOutput.THREAD_CREATED
    elif p[1] == "thread-group-created":
        p[0] = GdbOutput.THREAD_GROUP_CREATED
    elif p[1] == "thread-group-added":
        p[0] = GdbOutput.THREAD_GROUP_ADDED
    elif p[1] == "thread-group-started":
        p[0] = GdbOutput.THREAD_GROUP_STARTED
    elif p[1] == "thread-exited":
        p[0] = GdbOutput.THREAD_EXITED
    elif p[1] == "thread-group-exited":
        p[0] = GdbOutput.THREAD_GROUP_EXITED
    elif p[1] == "thread-selected":
        p[0] = GdbOutput.THREAD_SELECTED
    elif p[1] == "library-loaded":
        p[0] = GdbOutput.LIBRARY_LOADED
    elif p[1] == "library-unloaded":
        p[0] = GdbOutput.LIBRARY_UNLOADED
    elif p[1] == "breakpoint-modified":
        p[0] = GdbOutput.BREAKPOINT_MODIFIED
    elif p[1] == "breakpoint-created":
        p[0] = GdbOutput.BREAKPOINT_CREATED
    else:
        raise helpers.excep.GdbError("Got " + p[1] + " which cannot occur here!")


def p_result(p):
    '''result : variable ASSIGN value'''
    p[0] = Assignment(p[1], p[3])


def p_variable(p):
    '''variable : STRING'''
    p[0] = p[1]


def p_value(p):
    '''value : const
             | tuple_
             | list_'''
    p[0] = p[1]


def p_const(p):
    '''const : C_STRING'''
    p[0] = p[1]


def p_tuple_(p):
    '''tuple_ : LBRACE RBRACE
              | LBRACE result_list RBRACE'''
    if len(p) > 3:
        p[0] = Result()
        for a in p[2]:
            setattr(p[0], a.dest, a.src)
    else:
        p[0] = []


def p_list_(p):
    '''list_ : LBRACKET RBRACKET
             | LBRACKET value_list RBRACKET
             | LBRACKET result_list RBRACKET'''
    if len(p) > 3:
        p[0] = p[2]
    else:
        p[0] = []


def p_stream_output(p):
    '''stream_output : C_STRING'''
    p[0] = GdbOutput()
    p[0].string = p[1]


def p_result_list(p):
    '''result_list : result
                   | result COMMA result_list'''
    if len(p) > 2:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_value_list(p):
    '''value_list : value
                  | value COMMA value_list'''
    if len(p) > 2:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


def p_error(p):
    if p:
        raise helpers.excep.GdbError("Syntax error in input, line %d, col %d: %s", \
            p.lineno, p.lexpos, p.type)
    else:
        raise helpers.excep.GdbError("Syntax error in input!")


def p_top(p):
    '''top : HAT result_record
           | STAR async_output
           | PLUS async_output
           | ASSIGN async_output
           | TILDE stream_output
           | AT stream_output
           | AMP stream_output'''

    p[0] = p[2]
    if p[1] == '^':
        p[0].type_ = GdbOutput.RESULT_RECORD
    elif p[1] == '*':
        p[0].type_ = GdbOutput.EXEC_ASYN
    elif p[1] == '+':
        p[0].type_ = GdbOutput.STATUS_ASYN
    elif p[1] == '=':
        p[0].type_ = GdbOutput.NOTIFY_ASYN
    elif p[1] == '~':
        p[0].type_ = GdbOutput.CONSOLE_STREAM
    elif p[1] == '@':
        p[0].type_ = GdbOutput.TARGET_STREAM
    elif p[1] == '&':
        p[0].type_ = GdbOutput.LOG_STREAM


class GdbResultParser:
    @classmethod
    def parse(cls, lines):
        """Parse the lines with the above defined lexical rules
        """
        lex.lex(reflags=re.DOTALL)

        parser = yacc.yacc(start='top', debug=0, outputdir=str(QDir.homePath()) + "/.ricodebug")
        r = []
        for line in lines:
            line = line.strip()
            r.append(parser.parse(line))
            r[-1].raw = line

        return r
