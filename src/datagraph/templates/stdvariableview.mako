<%namespace name="common" file="/common.mako"/>\
<%call expr="common.simple_entry(role, id, 'var.png', varWrapper)">
	${varWrapper.getValue() | h}
</%call>
