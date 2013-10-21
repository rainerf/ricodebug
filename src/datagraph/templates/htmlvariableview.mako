<%!
  from datagraph.datagraphvariables import Role
%>\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
span.vartype { color: rgb(0, 0, 120); vertical-align:top; }
span.varname { font-weight: bold; vertical-align:top; }
span.varaccess { color: rgb(90, 90, 90); vertical-align:top; }
span.gdbconsole_output_ok { color: green; }
span.gdbconsole_output_error { color: red; }
table { border-spacing: 0pt; }
td {padding: 2pt; white-space: nowrap; }
td.vartype {vertical-align:top;}
td.varname {vertical-align:top;}
td.varaccess {vertical-align:top;}
td.varvalue {vertical-align:top;}
td.open_close {vertical-align:top;}
td.withborder { border-left: 1pt solid; border-left-color: rgba(200, 200, 200, 1)}
table.variabletop {border: 1pt solid rgba(200, 200, 200, 1); background: rgba(255, 255, 255, 1); position: absolute; left:0px; top:0px; border-radius:5px;}
table.variablechild {border: 1pt solid rgba(200, 200, 200, 1); border-radius:5px;}
div.removediv {position:absolute; left:2px; top:2px; z-index:1; opacity:0.2}
div.removediv:hover {opacity:1;}
tr.header {background: -webkit-linear-gradient(top, rgba(220,220,220,1) 0%,rgba(255,255,255,1) 100%); border: 0;}
a {border-bottom:1px dotted;}
* {-webkit-user-select: none; user-select: none; font-family: sans-serif;}
input {-webkit-user-select: text; user-select: text; border: 1px solid rgba(200, 200, 200, 1); }
form {margin: 0px; }
</style>
<script type="text/javascript">
function contextmenu(obj, id) {
  document.getElementById(id).style.background = 'rgba(245, 245, 245, 1)';
  obj.openContextMenu();
  event.stopPropagation();
  document.getElementById(id).style.background = '';
}
function showChangeInput(obj, td) {
  document.getElementById(td).innerHTML="<form onsubmit='setValue(" + obj + ", \"" + td + "\"); return false;'><input type='text' id='valueinput' value=" + document.getElementById(td).innerHTML + "></form>";
  document.getElementById(td).ondblclick = null;
}
function setValue(obj, td) {
  value = document.getElementById("valueinput").value;
  obj.setValue(value);
}
</script>
</head>
<body>
<% assert(top) %>\
%  if var.inScope:
<table class="variabletop">
${var.render(Role.INCLUDE_HEADER)}
</table>
<div class="removediv">
<img alt="" onclick="${id}.remove()" src="qrc:icons/images/exit.png" width="16px" height="16px" />
</div>
%  endif
</body>
</html>
