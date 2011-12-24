<!-- show variable if its in scope: -->
	<tr id="${id}" oncontextmenu="contextmenu(${id}, '${id}')";>
		<td nowrap>
%		if top:
			<a ondblclick="${id}.remove()">x</a>
%		endif
			<img src="qrc:icons/images/var.png">
%		if varWrapper.getAccess():
			<span class="graph_access"> ${varWrapper.getAccess()} </span>
%		endif
		</td>
		<td nowrap>
			<span class="graph_typename"> ${varWrapper.getType()} </span>
		</td>
		<td nowrap>
			<span class="graph_varname"> ${varWrapper.getExp()} </span>
		</td>
		<td nowrap>
			= 
		</td>
		<td nowrap>
			<a ondblclick="${id}.dereference()">${varWrapper.getValue()}</a>
		</td>
	</tr>
