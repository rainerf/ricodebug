<%!
	import matplotlib.pyplot as plt
	import time
	import os
	from PyQt4 import QtCore
%>\
<%namespace name="common" file="/common.mako"/>\
<%
	g = "%s/g%s%d.svg" % (str(QtCore.QDir.tempPath()), id, os.getpid())
	fig = plt.figure(figsize=(4, 3))
	ax = fig.add_subplot(111)
	ax.plot(data)
	fig.savefig(g, format='svg', transparent=True, bbox_inches='tight')
%>\
<%call expr="common.complex_entry(top, id, 'struct.png', varWrapper)">
<tr><td>
<img src="file://${g}?${time.time()}" />
</td></tr>
</%call>
