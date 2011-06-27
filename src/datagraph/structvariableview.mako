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
     <a href="${str(var)};remove">x</a> &nbsp;
    % endif
    % if var.getAccess() != None:
     ${var.getAccess()}
    % endif
    <span class="graph_typename"> ${var.getType()} </span> &nbsp; <span class="graph_varname"> ${var.getExp()} </span>
    % if len(var.getChildren()) > 0:
	   % if var.isOpen:
	   		&nbsp; &nbsp; <a href="${str(var)};close">-</a>
	   % else:
	        = <a href="${str(var)};open">...</a>
	   % endif
    % else:
   	 = ${var.getValue()}
    % endif
   </td>
  </tr>
 % if var.isOpen:
  <tr>
   <td>
    <table border="0" cellspacing="0" cellpadding="2">
 	 % for childVW in var.getChildren():
     <tr>
      <td>
       ${childVW.getTemplateHandler().render(handlers)}
      </td>
     </tr>
 	 % endfor
 	</table>
   </td>
  </tr>
 % endif
 </table>
% endif
