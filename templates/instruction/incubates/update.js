$('#instruction-dialog').modal('toggle');

$('#sequence-{{sequence}}').replaceWith(`{%- include 'instruction/incubates/_incubates.html' -%}`);
