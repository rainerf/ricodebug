<%!
	from datagraph.datagraphvw import Role
%>\
<%namespace name="common" file="/common.mako"/>\
<%call expr="common.complex_entry(role, id, 'struct.png', varWrapper)">
%	if vertical:
%		for childVW in varWrapper.getChildren():
		${childVW.render(Role.NORMAL)}
%		endfor
%	else:
%		for idx, childVW in enumerate(varWrapper.getChildren()):
		<td nowrap title="${childVW.getAccess() | h} ${childVW.getType() | h} ${childVW.getExp() | h}" ${'class="withborder"' if idx != 0 else ''}>
		${childVW.render(Role.VALUE_ONLY)}
		</td>
%		endfor
%	endif
</%call>
