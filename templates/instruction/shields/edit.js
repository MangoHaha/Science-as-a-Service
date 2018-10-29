$('#instruction-dialog').modal( {observeChanges: true}).modal("show");
{% set route = '/protocol/' + shields['protocol_id']|string + '/instruction/' + shields['sequence']|string + '/shields' %}
{% with method='PATCH', route = route, seal = shields['seal'], reverse = shields['reverse'] %}
  {% include "instruction/shields/form.js"%}
{% endwith %}

$('.instruction.modal.header').html("Edit a shield!");
{% set sample_id = shields['sample_id']|string %}
$('#shield_sample_id').dropdown('set selected', {{sample_id}});
