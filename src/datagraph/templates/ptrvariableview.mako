<%namespace name="common" file="/common.mako"/>\
<%call expr="common.simple_entry(role, id, 'var.png', varWrapper, allowEdit=False)">
	<a ondblclick="${id}.dereference()">${varWrapper.value | h}</a>
</%call>
