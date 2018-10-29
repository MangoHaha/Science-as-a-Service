$('#instruction-dialog').modal('toggle');

$('#sequence-{{sequence}}').replaceWith(`{%- include 'instruction/transfers/_transfers.html' -%}`);
