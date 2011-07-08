<html>
<body>
<style>
span.graph_typename { color: blue; font-style: italic; }
span.graph_varname { font-weight: bold; }
span.gdbconsole_output_ok { color: green; }
span.gdbconsole_output_error { color: red; }
table { border-spacing: 0 }
table.variabletop {border: 1pt solid blue; background-image: url('qrc:graph/images/background.png'); position: absolute; left:0px; top:0px; }
table.variablechild {border: 1pt solid blue;}
tr.header {background-color: #ffffff; border: 0;} 
a {border-bottom:1px dotted;}
* {-webkit-user-select: none; user-select: none}
</style>
<script type="text/javascript">
function contextmenu(obj, id) {
	document.getElementById(id).style.background = '#ffffff';
	obj.openContextMenu();
	event.stopPropagation();
	document.getElementById(id).style.background = '';
}
</script>
%	if varWrapper.getInScope() == True:
%		if top:
<table class="variabletop" oncontextmenu="{$id}.openContextMenu();">
%		endif
${varWrapper.render(top)}
%		if top:
</table>
%		endif
%	endif
</body>
</html>
