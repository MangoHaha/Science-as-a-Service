$('#instruction-dialog').modal( {observeChanges: true}).modal("show");
{% set route = '/protocol/' + transfers['protocol_id']|string + '/instruction/' + transfers['sequence']|string + '/transfers' %}
{% with method='PATCH', route = route, duration = transfers['duration'],
    temperature = transfers['temperature'], type = transfers['type'], wells = transfers['wells'],
    to_sample_id = transfers['to_sample_id'], from_sample_id = transfers['from_sample_id'],
    aspirate_speed = transfers['aspirate_speed'], dispense_speed = transfers['dispense_speed'] %}
  {% include "instruction/transfers/form.js"%}
{% endwith %}

$('.instruction.modal.header').html("Edit a transfer!");
{% set from_sample_id = transfers['from_sample_id']|string %}
{% set to_sample_id = transfers['to_sample_id']|string %}
$('#transfers_from_sample_id').dropdown('set selected', {{from_sample_id}});
$('#transfers_to_sample_id').dropdown('set selected', {{to_sample_id}});
