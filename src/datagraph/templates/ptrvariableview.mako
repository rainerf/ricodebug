<%namespace name="common" file="/common.mako"/>\
<%call expr="common.simple_entry(role, id, 'var.png', var, allowEdit=False)">
	<a ondblclick="${id}.dereference()">${var.value | h}</a>
</%call>
