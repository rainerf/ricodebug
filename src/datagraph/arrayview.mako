<%!
	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt
	import time
	import os
	from PyQt4 import QtCore
%>\
<%def name="main()">
<%
	g = "%s/g%s%d.svg" % (str(QtCore.QDir.tempPath()), id, os.getpid())
	fig = plt.figure(figsize=(4, 3))
	ax = fig.add_subplot(111)
	ax.plot(data)
	fig.savefig(g, format='svg', transparent=True, bbox_inches='tight')
%>\
<img src="file://${g}?${time.time()}" />
</%def>
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
${main()}
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
${main()}
			</table>
		</td>
	</tr>
%		endif
