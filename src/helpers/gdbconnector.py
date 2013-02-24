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

import subprocess
import signal
import logging
import time

from PyQt4.QtCore import QObject, pyqtSignal

from .gdbreader import GdbReader
from .gdboutput import GdbOutput
import helpers


class GdbConnector(QObject):
    commandExecuted = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', float)

    def __init__(self):
        QObject.__init__(self)
        self.__gdb = None
        self.reader = GdbReader(self)

    def start(self):
        self.kill()

        try:
            self.__gdb = subprocess.Popen(['gdb', '-i', 'mi', '-q', '-nx'], \
                    shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except OSError as e:
            logging.critical("Could not start _gdb. Error message: %s", e)
        self.reader.startReading(self.__gdb.stdout)

    def kill(self):
        if self.__gdb:
            self.__gdb.kill()

    def execute(self, cmd, error_msg=None):
        __start = time.time()

        logging.debug("Running command %s", cmd)
        self.__gdb.stdin.write(cmd + "\n")
        res = self.reader.getResult(GdbOutput.RESULT_RECORD)

        if res.class_ == GdbOutput.ERROR:
            logging.debug("Command '%s' failed with %s (%s, '%s')",
                    cmd, res.msg, res.raw, error_msg)

        self.commandExecuted.emit(cmd, res, time.time() - __start)

        return res

    def executeAndRaiseIfFailed(self, cmd, error_msg=None):
        res = self.execute(cmd, error_msg)

        if res.class_ == GdbOutput.ERROR:
            logging.error(res.msg)
            if error_msg:
                logging.error("%s\n%s", error_msg, res.msg)
            raise helpers.excep.GdbError(res.msg)

        return res

    def setTty(self, tty):
        self.executeAndRaiseIfFailed("-inferior-tty-set " + tty,
                "Could not set target's TTY!")

    def openFile(self, filename):
        self.executeAndRaiseIfFailed("-file-exec-and-symbols " + filename,
                "Could not open file!")

    def getSources(self):
        res = self.executeAndRaiseIfFailed("-file-list-exec-source-files",
                "Could not get files.")

        files = []
        for f in res.files:
            if hasattr(f, "fullname"):
                files.append(f.fullname)

        # gdb reports some files multiple times, uniqify the list
        s = set(files)
        files = list(s)

        return files

    def getMultipleBreakpoints(self, nr):
        res = self.executeAndRaiseIfFailed("info break " + str(nr),
                "Could not get multiple breakpoint list.")
        return res

    def getBreakpoints(self):
        res = self.executeAndRaiseIfFailed("-break-list",
                "Could not get breakpoint list.")

        breakpoints = []
        for bp in res.BreakpointTable.body:
            if not hasattr(bp, "fullname"):
                bp.fullname = "n/a"
            breakpoints.append(bp.src)

        return breakpoints

    def getLocals(self):
        res = self.executeAndRaiseIfFailed("-stack-list-variables --no-values")

        variables = []

        if hasattr(res, "variables"):
            for v in res.variables:
                if not hasattr(v, "arg"):
                    v.arg = False
                else:
                    v.arg = True
                variables.append(v)

        return variables

    def getStack(self, thread_id=None):
        if thread_id:
            res = self.executeAndRaiseIfFailed("-stack-list-frames --thread %s" % thread_id)
        else:
            res = self.executeAndRaiseIfFailed("-stack-list-frames")

        stack = []

        if not hasattr(res, "stack"):
            return stack

        for f in res.stack:
            stack.append(f.src)

        return stack

    def insertWatchpoint(self, exp):
        addr = self.evaluate("&" + exp)
        if not addr:
            logging.error("Cannot set watchpoint for '%s'." % exp)
        else:
            return self.executeAndRaiseIfFailed("-break-watch *" + addr)

    def insertBreakpoint(self, loc, line):
        if line is not None:
            loc = "%s:%s" % (loc, str(line))
        return self.executeAndRaiseIfFailed("-break-insert " + loc,
                "Could not create breakpoint " + loc + ".")

    def deleteBreakpoint(self, number):
        return self.executeAndRaiseIfFailed("-break-delete " + str(number))

    def enableBreakpoint(self, number):
        return self.executeAndRaiseIfFailed("-break-enable " + str(number),
                "Could not enable breakpoint " + str(number) + ".")

    def disableBreakpoint(self, number):
        return self.executeAndRaiseIfFailed("-break-disable " + str(number),
                "Could not disable breakpoint " + str(number) + ".")

    def setSkipBreakpoint(self, number, skip):
        return self.executeAndRaiseIfFailed("-break-after " + str(number) +
                " " + str(skip), "Could not set breakpoint interval '" +
                str(skip) + "' for breakpoint " + str(number) + ".")

    def setConditionBreakpoint(self, number, condition):
        return self.executeAndRaiseIfFailed("-break-condition " + str(number)
                + " " + str(condition), "Could not set condition '" +
                str(condition) + "' for breakpoint " + str(number) + ".")

    def changeWorkingDirectory(self, dir_):
        return self.executeAndRaiseIfFailed("-environment-cd " + dir_)

    def setArgs(self, args):
        if args is not None:
            args = '"%s"' % args
        else:
            args = ""
        return self.executeAndRaiseIfFailed("-exec-arguments " + args,
                "Failed to set arguments")

    def run(self):
        return self.executeAndRaiseIfFailed("-exec-run",
                "Could not run the program.")

    def record_start(self):
        """Start recording

        Records the call stack and gdb executions for reverse debugging
        """
        # FIXME: find the real mi command!
        return self.executeAndRaiseIfFailed("-interpreter-exec console rec",
                "Could not record the process.")

    def record_stop(self):
        """Stop recording
        """
        # FIXME: find the real mi command!
        return self.executeAndRaiseIfFailed(
                "-interpreter-exec console \"record stop\"",
                "Could not record the process.")

    def next_(self):
        return self.executeAndRaiseIfFailed("-exec-next")

    def reverse_next(self):
        return self.executeAndRaiseIfFailed("-exec-next --reverse")

    def step(self):
        return self.executeAndRaiseIfFailed("-exec-step")

    def reverse_step(self):
        return self.executeAndRaiseIfFailed("-exec-step --reverse")

    def cont(self):
        return self.executeAndRaiseIfFailed("-exec-continue")

    def reverse_cont(self):
        return self.executeAndRaiseIfFailed("-exec-continue --reverse")

    def interrupt(self):
        # TODO: check if it also works in windows
        self.__gdb.send_signal(signal.SIGINT)
        # return self.executeAndRaiseIfFailed("-exec-interrupt")

    def finish(self):
        return self.executeAndRaiseIfFailed("-exec-finish")

    def until(self, file_, line):
        loc = file_ + ":" + str(line)
        return self.executeAndRaiseIfFailed("-exec-until " + loc)

    def evaluate(self, exp):
        res = self.execute("-data-evaluate-expression " + exp)
        if res.class_ == GdbOutput.ERROR:
            return None
        else:
            return res.value

    def executeCliCommand(self, cmd):
        res = self.execute("-interpreter-exec console \"" + cmd + "\"")
        if res.class_ == GdbOutput.ERROR:
            return res.msg
        else:
            return None

    def var_create(self, exp):
        return self.execute("-var-create - * \"" + exp + "\"")

    def var_delete(self, exp):
        return self.execute("-var-delete \"" + exp + "\"")

    def var_assign(self, exp, value):
        return self.execute("-var-assign \"" + exp + "\" " + value)

    def var_list_children(self, exp):
        return self.execute("-var-list-children --all-values \"" +
                str(exp) + "\"")

    def var_update(self, exp):
        return self.execute("-var-update --all-values \"" + exp + "\"")

    def getStackDepth(self):
        res = self.execute("-stack-info-depth")
        if res.class_ == GdbOutput.ERROR:
            return None
        else:
            return int(res.depth)

    def selectStackFrame(self, exp):
        return self.executeAndRaiseIfFailed("-stack-select-frame " + str(exp))

    def threadInfo(self):
        return self.executeAndRaiseIfFailed("-thread-info")

    def selectThread(self, id_):
        return self.executeAndRaiseIfFailed("-thread-select %s" % id_)
