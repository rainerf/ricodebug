<!-- show variable if its in scope: -->
%		if top:
	<tr class="header">
		<td nowrap>
			<a ondblclick="${id}.remove()">x</a>
			<img src="qrc:icons/images/struct.png">
			<span class="graph_typename"> ${var.getType()} </span>
			<a ondblclick="${id}.${"close" if var.isOpen else "open"}()">
			<span class="graph_varname"> ${var.getExp()}</span></a>
%			if not var.isOpen:
				=
		</td>
		<td>
			<a ondblclick="${id}.open()">
			<table class="variablechild"><tr><td>...</td></tr></table>
			</a>
%			endif
		</td>
	</tr>
%			if var.isOpen:
	<tr>
		<td nowrap>
			<table>
%				for childVW in var.getChildren():
				${childVW.getTemplateHandler().render(view, False, parentHandler)}
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
%		if var.getAccess() != None:
			${var.getAccess()}
%		endif
		</td>
		<td nowrap>
			<span class="graph_typename"> ${var.getType()} </span>
		</td>
		<td nowrap>
			<a ondblclick="${id}.${"close" if var.isOpen else "open"}()">
			<span class="graph_varname"> ${var.getExp()}</span></a>
		</td>
		<td nowrap>
			=
		</td>
		<td nowrap>
			<table class="variablechild">
%		if var.isOpen:
%			for childVW in var.getChildren():
				${childVW.getTemplateHandler().render(view, False, parentHandler)}
%			endfor
%		else:
			<tr><td>...</td></tr>
%		endif
			</table>
		</td>
	</tr>
%		endif
