$('#equipment-dialog').modal('toggle');

$('#equipment-{{id}}').replaceWith(`{%- include 'equipment/_equipment.html' -%}`);

$('.ui.safety-level.rating').rating({ maxRating: 3 });
$('.ui.safety-level.rating').rating('disable');
