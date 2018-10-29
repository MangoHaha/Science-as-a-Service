$('#instruction-dialog').modal('toggle');

$('#sequence-{{sequence}}').replaceWith(`{%- include 'instruction/spectros/_spectros.html' -%}`);
