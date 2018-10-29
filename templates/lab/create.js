$('#lab-dialog').modal('toggle');

$('#lab-list').append(`{%- include 'lab/_lab.html' -%}`);

$('.ui.safety-level.rating').rating({ maxRating: 3 });
$('.ui.safety-level.rating').rating('disable');
