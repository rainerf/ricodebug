<%namespace name="common" file="/common.mako"/>\
<%call expr="common.simple_entry(role, id, 'var.png', varWrapper)">
	<a ondblclick="${id}.dereference()">${varWrapper.getValue() | h}</a>
</%call>
