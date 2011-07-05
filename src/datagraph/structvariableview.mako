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
	<tr>
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
	<tr oncontextmenu="${id}.openContextMenu(); event.stopPropagation();">
		<td nowrap>
			<img src="qrc:icons/images/struct.png">
%		if varWrapper.getAccess():
			${varWrapper.getAccess()}
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
