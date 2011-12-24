<!-- show variable if its in scope: -->
%		if top:
	<tr class="header">
		<td nowrap>
			<a ondblclick="${id}.remove()">x</a>
			<img src="qrc:icons/images/struct.png">
			<span class="graph_typename"> ${varWrapper.getType()} </span>
			<a ondblclick="${id}.${"close" if varWrapper.isOpen else "open"}()">
			<span class="graph_varname"> ${varWrapper.getExp()}</span></a>
%			if not varWrapper.isOpen:
				=
		</td>
		<td>
			<a ondblclick="${id}.open()">
			<table class="variablechild"><tr><td>...</td></tr></table>
			</a>
%			endif
		</td>
	</tr>
%			if varWrapper.isOpen:
	<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')";>
		<td nowrap>
			<table>
%				for childVW in varWrapper.getChildren():
				${childVW.render(False)}
%				endfor
			</table>
		</td>
	</tr>
%			endif
##
%		else:
##
	<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')";>
		<td nowrap>
			<img src="qrc:icons/images/struct.png">
%		if varWrapper.getAccess():
			<span class="graph_access"> ${varWrapper.getAccess()} </span>
%		endif
		</td>
		<td nowrap>
			<span class="graph_typename"> ${varWrapper.getType()} </span>
		</td>
		<td nowrap>
			<a ondblclick="${id}.${"close" if varWrapper.isOpen else "open"}()">
			<span class="graph_varname"> ${varWrapper.getExp()}</span></a>
		</td>
		<td nowrap>
			=
		</td>
		<td nowrap>
			<table class="variablechild">
%		if varWrapper.isOpen:
%			for childVW in varWrapper.getChildren():
				${childVW.render(False)}
%			endfor
%		else:
			<tr><td>...</td></tr>
%		endif
			</table>
		</td>
	</tr>
%		endif
