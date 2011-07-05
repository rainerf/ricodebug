<%!
	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt
	import time
	import os
	from PyQt4 import QtCore
%>\
<!-- show variable if its in scope: -->
%		if top:
	<tr class="header">
		<td nowrap>
			<a ondblclick="${id}.remove()">x</a>
			<img src="qrc:icons/images/struct.png" />
			<span class="graph_typename"> ${varWrapper.getType()} </span>
			<span class="graph_varname"> ${varWrapper.getExp()}</span></a>
		</td>
	</tr>
	<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')";>
		<td nowrap>
			<table>
<%
	g = "%s/g%s%d.png" % (str(QtCore.QDir.tempPath()), id, os.getpid())
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(data)
	fig.savefig(g)
%>\
				<img src="file://${g}?${time.time()}" oncontextmenu="${id}.openContextMenu(); event.stopPropagation();" />
			</table>
		</td>
	</tr>
##
%		else:
##
	<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')";>
		<td nowrap>
			<img src="qrc:icons/images/struct.png" />
%		if varWrapper.getAccess():
			${varWrapper.getAccess()}
%		endif
		</td>
		<td nowrap>
			<span class="graph_typename"> ${varWrapper.getType()} </span>
		</td>
		<td nowrap>
			<span class="graph_varname"> ${varWrapper.getExp()}</span></a>
		</td>
		<td nowrap>
			=
		</td>
		<td nowrap>
			<table class="variablechild">
<%
	g = "%s/g%s%d.png" % (str(QtCore.QDir.tempPath()), id, os.getpid())
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(data)
	fig.savefig(g)
%>\
				<img src="file://${g}?${time.time()}" oncontextmenu="${id}.openContextMenu(); event.stopPropagation();" />
			</table>
		</td>
	</tr>
%		endif
