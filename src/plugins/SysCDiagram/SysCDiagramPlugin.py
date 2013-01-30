# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphes and SystemC features.
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

from PyQt4.QtCore import QThread
from datagraph.svgview import SVGDataGraphVW
from datagraph.SVGImage import SVGImage
from StringIO import StringIO
from pydot import Dot, Cluster, Node

from variables.varwrapperfactory import VarWrapperFactory
from variables.variablelist import VariableList


class SysCDiagramPlugin(QThread):

    def __init__(self):
        QThread.__init__(self, None)

    def initPlugin(self, signalproxy):
        """Initialise the systemc block diagram plugin"""

        self.signalproxy = signalproxy
        self.do = signalproxy.distributedObjects

        # systemc stuff and and pointer type strings needed for casting in gdb
        # because systemc objects can be systemc modules, systemc ports, etc.
        self.ctx = None
        self.ctx_pointer = None
        self.ctx_func = "sc_get_curr_simcontext()"
        self.ctx_found = False

        self.ctx_type = "(sc_core::sc_simcontext*)"
        self.port_type = "(sc_core::sc_port_base*)"
        self.module_type = "(sc_core::sc_module*)"
        self.object_type = "(sc_core::sc_object*)"
        self.prim_channel_type = "(sc_core::sc_prim_channel*)"

        # dict with a string that represents the pointer as key and
        # a nested dict with parent, children, etc as key-values
        #   dst_dict[ptr] = {"wrapper":    vw,
        #                    "name":       None,
        #                    "parent_ptr": None,
        #                    "children":   {}}
        self.sysc_modules = {}
        self.sysc_objects = {}
        self.sysc_ports = {}
        self.sysc_prim_channels = {}

        # because of how we built the interface for the tracepoints on the
        # datagraph we first need to create an file obj. We choose StringIO
        # because it uses a string as buffer and does not acces the filesystem
        self._file_obj = StringIO()
        self.image = SVGImage("SystemC Block Diagram", self._file_obj)
        self.image_wrapper = SVGDataGraphVW(self.image, self.do)

        self.signalproxy.inferiorStoppedNormally.connect(self.update)

        # hook Datagraph variable wrapper into the datagraph controller
        # after self.action.commit is called the image will be displayed at the
        # datagraph
        self.action = self.do.actions.\
            getAddSVGToDatagraphAction(self.image_wrapper,
                                       self.do.
                                       datagraphController.addVar)

        # pydot graph visualization library
        self.block_diagram = Dot(graph_type='digraph')
        self.block_diagram.set_graph_defaults(compound='true',
                                              splines='ortho',
                                              rankdir='LR')
        self.block_diagram.set_node_defaults(shape='box')

        # Needed for creating the right variables and variable wrappers from
        # the systemc pointers
        self.vwFactory = VarWrapperFactory()
        self.variableList = VariableList(self.vwFactory, self.do)

    def deInitPlugin(self):
        pass

    def evaluateExp(self, exp):
        return self.signalproxy.gdbEvaluateExpression(exp)

    def showDiagram(self):
        self.action.commit()

    def update(self):
        self.start()

    def run(self):
        if not self.ctx_found:
            self.__findSimContext()
        else:
            # don't try to analyze if elaboration is not done
            if not self.ctx["m_elaboration_done"]:
                return

        # prepare for easy information collection
        object_vec = self.ctx["m_child_objects"]

        # find all relevant information
        self.__findSysCObjects(object_vec, self.object_type, self.sysc_objects)

        clusters = {}
        nodes = {}

        # build pydot hierachy and add all subgraphs and nodes to the main
        # graph
        self.__buildHierachy(self.sysc_objects, clusters, nodes)
        for sptr in clusters:
            self.block_diagram.add_subgraph(clusters[sptr])
        for sptr in nodes:
            self.block_diagram.add_node(nodes[sptr])

        self.block_diagram.write_raw("bd.gv")
        self._file_obj.write(self.block_diagram.create_svg())
        self.signalproxy.inferiorStoppedNormally.disconnect(self.update)

        self.showDiagram()

    def __buildHierachy(self, obj_dict, clusters, nodes):
        """ Build Cluster and Node hierachy for pydot
        """
        for ptr in obj_dict:
            obj = obj_dict[ptr]
            if ptr in (self.sysc_ports.keys()+self.sysc_prim_channels.keys()):
                continue

            if len(obj["children"].keys()) == 0:
                node = Node(obj["name"])
                nodes[ptr] = node
            else:
                clust = Cluster(obj["name"].replace(".", "_"),
                                color='red',
                                label=obj["name"])
                c_clusters = {}
                c_nodes = {}
                self.__buildHierachy(obj["children"], c_clusters, c_nodes)
                for sptr in c_clusters:
                    clust.add_subgraph(c_clusters[sptr])
                for sptr in c_nodes:
                    clust.add_node(c_nodes[sptr])
                clusters[ptr] = clust

    def __findSysCObjects(self, obj_vec, obj_type, dst_dict):
        """ Find sc_object from module, port and prim channel registry
        """
        for i in obj_vec.childs:
            ptr = i.value
            var = "(*{}{})".format(obj_type, ptr)
            vw = self.variableList.addVarByName(var)
            dst_dict[ptr] = {"wrapper":    vw,
                             "name":       None,
                             "parent_ptr": None,
                             "children":   {}}

            for member in vw.childs:
                if member.exp == "m_name":
                    dst_dict[ptr]["name"] = member.value.strip('"')

                elif member.exp == "m_child_objects":
                    children = {}
                    self.__findSysCObjects(vw["m_child_objects"],
                                           obj_type,
                                           children)
                    dst_dict[ptr]["children"] = children

                elif member.exp == "m_parent":
                    dst_dict[ptr]["parent_ptr"] = member.value

    def __findSimContext(self):
        """ Find systemc simulation context
        """
        self.ctx_pointer = self.evaluateExp(self.ctx_func)
        if self.ctx is None:
            frame = 0
            depth = self.signalproxy.gdbGetStackDepth()
            while (self.ctx_pointer is None) and frame <= depth:
                frame += 1
                self.signalproxy.gdbSelectStackFrame(frame)
                self.ctx_pointer = self.evaluateExp(self.ctx_func)
            else:
                if self.ctx_pointer is None:
                    return
                else:
                    self.ctx_found = True
                    self.ctx = self.do.variablePool.getVar(self.ctx_func)["*"]
        else:
            self.ctx_found = True
            self.ctx = self.do.variablePool.getVar(self.ctx_func)["*"]

