<%def name="open_close_entry(varWrapper)">
%	if varWrapper.isOpen:
		<img onclick="${id}.close()" src="qrc:icons/images/opened.png">
%	else:
		<img onclick="${id}.open_()" src="qrc:icons/images/closed.png">
%	endif
</%def>
##
###############################################################################
##
<%def name="simple_entry(id_, icon, varWrapper, openclose=False)">
	<tr id="${id_}" oncontextmenu="contextmenu(${id_}, '${id_}')";>
		<td nowrap>
			<img src="qrc:icons/images/${icon}">
%	if varWrapper.getAccess():
			<span class="graph_access"> ${varWrapper.getAccess()}</span>
%	endif
		</td>
		<td nowrap>
			<span class="graph_typename"> ${varWrapper.getType()}</span>
		</td>
		<td nowrap>
			<span class="graph_varname"> ${varWrapper.getExp()}</span>
		</td>
		<td nowrap>
%	if openclose:
			${open_close_entry(varWrapper)}
%	else:
			=
%	endif
		</td>
		<td nowrap>
			${caller.body()}
		</td>
	</tr>
</%def>\
##
###############################################################################
##
<%def name="complex_entry(top, id_, icon, varWrapper)">
%	if top:
	<tr class="header" id="${id}" oncontextmenu="contextmenu(${id}, '${id}')">
		<td nowrap>
			<img src="qrc:icons/images/${icon}">
			<span class="graph_typename"> ${varWrapper.getType()}</span> 
			<span class="graph_varname"> ${varWrapper.getExp()}</span>
			${open_close_entry(varWrapper)}
		</td>
	</tr>
%		if varWrapper.isOpen:
	<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')";>
		<td nowrap>
			<table>
				${caller.body()}
			</table>
		</td>
	</tr>
%		endif
##
%	else:
##
<%call expr="simple_entry(id, 'struct.png', varWrapper, True)">
			<table class="variablechild">
%		if varWrapper.isOpen:
				${caller.body()}
%		else:
			<tr><td>...</td></tr>
%		endif
			</table>
</%call>
%	endif
</%def>\
