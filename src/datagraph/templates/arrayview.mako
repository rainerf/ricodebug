<%!
	import time
	import os
	from PyQt4 import QtCore
	from datagraph.datagraphvariables import Role
%>\
<%namespace name="common" file="/common.mako"/>\
<%
	g = "%s/g%s%d.svg" % (str(QtCore.QDir.tempPath()), id, os.getpid())
	var.templateHandler.plot(g)
%>\
%	if role == Role.VALUE_ONLY:
<img alt="" src="file://${g}?${time.time()}" />
%	else:
<%call expr="common.complex_entry(role, id, 'struct.png', var)">
<tr><td>
<img alt="" src="file://${g}?${time.time()}" />
</td></tr>
</%call>
%	endif
