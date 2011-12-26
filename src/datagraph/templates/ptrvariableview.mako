<%namespace name="common" file="/common.mako"/>\
<%call expr="common.simple_entry(id, 'var.png', varWrapper)">
	<a ondblclick="${id}.dereference()">${varWrapper.getValue()}</a>
</%call>
