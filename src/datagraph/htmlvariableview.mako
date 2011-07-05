<html>
<body>
<style>
span.graph_typename { color: blue; font-style: italic; }
span.graph_varname { font-weight: bold; }
span.gdbconsole_output_ok { color: green; }
span.gdbconsole_output_error { color: red; }
table.variabletop {border: 1pt solid blue; border: 0; background-image: url('file:///home/rainer/tmp/t.png'); }
table.variablechild {border: 1pt solid blue;}
tr.header {background-color: #ffffff; border: 0;} 
a {border-bottom:1px dotted;}
* {-webkit-user-select: none; user-select: none}
</style>

%	if var.getInScope() == True:
%		if top:
<table class="variabletop" oncontextmenu="{$id}.openContextMenu();">
%		endif
${var.getTemplateHandler().render(view, top, parentHandler)}
%		if top:
 	</table>
%		endif
%	endif

</body>
</html>
