<!-- show variable if its in scope: -->
%	if var.getInScope() == True:
%		if top:
<table class="variabletop">
%		endif
	<tr>
		<td nowrap>
%		if top:
			<a href="${str(var)};close">x</a>
%		endif
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
				${var.getValue()}
			</td>
		</tr>
%		if top:
 	</table>
%		endif
%	endif
