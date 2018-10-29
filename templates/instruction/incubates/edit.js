$('#instruction-dialog').modal( {observeChanges: true}).modal("show");
{% set route = '/protocol/' + incubates['protocol_id']|string + '/instruction/' + incubates['sequence']|string + '/incubates' %}
{% with method='PATCH', route = route, duration = incubates['duration'], temperature = incubates['temperature'], shaking = incubates['shaking'], co2_percent = incubates['co2_percent'] %}
  {% include "instruction/incubates/form.js"%}
{% endwith %}

$('.instruction.modal.header').html("Edit a incubate!");
{% set sample_id = incubates['sample_id']|string %}
$('#incubate_sample_id').dropdown('set selected', {{sample_id}});
