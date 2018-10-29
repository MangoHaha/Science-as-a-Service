$('#instruction-dialog').modal('toggle');

$('#sequence-{{sequence}}').replaceWith(`{%- include 'instruction/shields/_shields.html' -%}`);
