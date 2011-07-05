<!-- show variable if its in scope: -->
	<tr oncontextmenu="${id}.openContextMenu(); event.stopPropagation();">
		<td nowrap>
%		if top:
			<a ondblclick="${id}.remove()">x</a>
%		endif
			<img src="qrc:icons/images/var.png">
%		if varWrapper.getAccess():
			${varWrapper.getAccess()}
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
			${varWrapper.getValue()}
		</td>
	</tr>
