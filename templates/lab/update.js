$('#lab-dialog').modal('toggle');

$('#lab-{{id}}').replaceWith(`{%- include 'lab/_lab.html' -%}`);

$('.ui.safety-level.rating').rating({ maxRating: 3 });
$('.ui.safety-level.rating').rating('disable');
