$('#lab-dialog').modal( {observeChanges: true}).modal("show");
{% set route = '/labs/' + lab['id']|string %}
{% with method='PATCH', route = route, id = lab['id'], usage_fee = lab['usage_fee'],
  address = lab['address'], safety_level = lab['safety_level'], name = lab['name'], area = lab['area'], active = lab['active'] %}
  {% include "lab/form.js"%}
{% endwith %}

$('.lab.modal.header').html("Edit a lab!");
