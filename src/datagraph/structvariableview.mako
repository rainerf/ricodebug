<!-- show variable if its in scope: -->
%	if var.getInScope() == True:
##
%		if top:
<table class="variabletop">
	<tr class="header">
		<td nowrap>
		<a href="${str(var)};remove">x</a>
		<span class="graph_typename"> ${var.getType()} </span>
		<span class="graph_varname"> ${var.getExp()} </span>
%			if var.isOpen:
		&nbsp; &nbsp; <a href="${str(var)};close">-</a>
%			else:
			= <a href="${str(var)};open">...</a>
%			endif
		</td>
	</tr>
%			if var.isOpen:
	<tr>
		<td nowrap>
			<table>
%				for childVW in var.getChildren():
				${childVW.getTemplateHandler().render(handlers)}
%				endfor
			</table>
		</td>
	</tr>
</table>
%			endif
##
%		else:
##
	<tr>
		<td nowrap>
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
%		if var.isOpen:
			&nbsp; &nbsp; <a href="${str(var)};close">-</a>
			<table class="variablechild">
%			for childVW in var.getChildren():
				${childVW.getTemplateHandler().render(handlers)}
%			endfor
			</table>
%		else:
				<a href="${str(var)};open">...</a>
%		endif
		</td>
	</tr>
%		endif
%	endif
