<%!
	from datagraph.datagraphvariables import Role
%>\
<%namespace name="common" file="/common.mako"/>\
<%call expr="common.complex_entry(role, id, 'struct.png', var)">
%	if vertical:
%		for childVW in var.getChildren():
		${childVW.render(Role.NORMAL)}
%		endfor
%	else:
%		for idx, childVW in enumerate(var.getChildren()):
		<td title="${childVW.access | h} ${childVW.type | h} ${childVW.exp | h}" ${'class="withborder"' if idx != 0 else ''}>
		${childVW.render(Role.VALUE_ONLY)}
		</td>
%		endfor
%	endif
</%call>
