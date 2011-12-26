<%namespace name="common" file="/common.mako"/>\
<%call expr="common.complex_entry(top, id, 'struct.png', varWrapper)">
%	for childVW in varWrapper.getChildren():
		${childVW.render(False)}
%	endfor
</%call>
