$('#instruction-dialog').modal( {observeChanges: true}).modal("show");
{% set route = '/protocol/' + spectros['protocol_id']|string + '/instruction/' + spectros['sequence']|string + '/spectros' %}
{% with method='PATCH', route = route, temperature = spectros['temperature'], type = spectros['type'],
  duration = spectros['duration'], orbital = spectros['orbital'], amplitude = spectros['amplitude'],
  num_flashes = spectros['num_flashes'], wavelength = spectros['wavelength'],
  excitation = spectros['excitation'], emission=spectros['emission'], gain = spectros['gain'],
  wells = spectros['wells'] %}
  {% include "instruction/spectros/form.js"%}
{% endwith %}

$('.instruction.modal.header').html("Edit a spectrophotometric step!");
{% set sample_id = spectros['sample_id']|string %}
$('#spectros_sample_id').dropdown('set selected', {{sample_id}});
{% set type = spectros['type']|string %}
$('#spectros_type').dropdown('set selected', '{{type}}');
