<%!
	from datagraph.datagraphvariables import Role
%>\
##
###############################################################################
##
<%def name="open_close_entry(id_, var)">
%	if var.isOpen:
		<img alt="" style="padding-top:5px" onclick="${id_}.toggleCollapsed()" src="qrc:icons/images/opened.png" />
%	else:
		<img alt="" style="padding-top:5px" onclick="${id_}.toggleCollapsed()" src="qrc:icons/images/closed.png" />
%	endif
</%def>
##
###############################################################################
##
<%def name="simple_entry(role, id_, icon, var, openclose=False, allowEdit=True)">
%	if not role == Role.VALUE_ONLY:
	<tr id="${id_}" oncontextmenu="contextmenu(${id_}, '${id_}')">
		<td class="varaccess">
<%	if var.access in ['private', 'protected']:
		iconprefix = var.access + "_"
	else:
		iconprefix = ""
%>\
			<img alt="" src="qrc:icons/images/${iconprefix}${icon}" />
%		if var.access:
			<span class="varaccess"> ${var.access | h}</span>
%		endif
		</td>
		<td class="vartype">
			<span class="vartype"> ${var.type | h}</span>
		</td>
		<td class="varname">
			<span class="varname"> ${var.exp | h}</span>
		</td>
		<td class="open_close">
%		if openclose:
			${open_close_entry(id_, var)}
%		else:
			=
%		endif
		</td>
		<td class="varvalue" id="${id_}value" \
%		if allowEdit:
ondblclick="showChangeInput('${id_}', '${id_}value')" \
%		endif
>
			${caller.body()}\
		</td>
	</tr>
%	else:
		${caller.body()}
%	endif
</%def>\
##
###############################################################################
##
<%def name="complex_entry(role, id_, icon, var)">
%	if role == Role.INCLUDE_HEADER:
	<tr class="header" id="${id}_header" oncontextmenu="contextmenu(${id}, '${id}')">
		<td>
			<img alt="" src="qrc:icons/images/${icon}" />
			<span class="vartype"> ${var.type | h}</span> 
			<span class="varname"> ${var.exp | h}</span>
			${open_close_entry(id_, var)}
		</td>
	</tr>
%		if var.isOpen:
	<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')">
		<td>
			<table>
				${caller.body()}
			</table>
		</td>
	</tr>
%		endif
##
%	else:
##
<%call expr="simple_entry(role, id, 'struct.png', var, True)">
			<table class="variablechild">
%		if var.isOpen:
			${caller.body()}
%		else:
			<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')"><td>...</td></tr>
%		endif
			</table>
</%call>
%	endif
</%def>\
