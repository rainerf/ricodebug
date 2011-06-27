<!-- show variable if its in scope: -->
% if var.getInScope() == True:
 % if top:
 <table border="1" cellspacing="0" cellpadding="2">
 % else:
 <table border="0" cellspacing="0" cellpadding="2">
 % endif
  <tr>
   <td nowrap>
   % if top:
    <a href="${str(var)};close">x</a> &nbsp;
   % endif
	% if var.getAccess() != None:
     ${var.getAccess()} &nbsp;
	% endif
    <span class="graph_typename"> ${var.getType()} </span> &nbsp;
    <span class="graph_varname"> ${var.getExp()} </span>
    = <a href="${str(var)};dereference">${var.getValue()}</a>
   </td>
  </tr>
 </table>
% endif
