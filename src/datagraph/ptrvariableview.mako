<!-- show variable if its in scope: -->
	<tr oncontextmenu="${id}.openContextMenu(); event.stopPropagation();">
		<td nowrap>
%		if top:
			<a ondblclick="${id}.remove()">x</a>
%		endif
			<img src="qrc:icons/images/var.png">
%		if var.getAccess() != None:
			${var.getAccess()}
%		endif
		</td>
		<td nowrap>
			<span class="graph_typename"> ${var.getType()} </span>
		</td>
		<td nowrap>
			<span class="graph_varname"> ${var.getExp()} </span>
		</td>
		<td nowrap>
			= 
		</td>
		<td nowrap>
			<a ondblclick="${id}.dereference()">${var.getValue()}</a>
		</td>
	</tr>
