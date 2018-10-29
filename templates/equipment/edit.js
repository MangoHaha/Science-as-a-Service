$('#equipment-dialog').modal( {observeChanges: true}).modal("show");
{% set route = '/equipment/' + equipment['id']|string %}
{% with method='PATCH', route = route, id = equipment['id'], lab_id = equipment['lab_id'],
  description = equipment['description'], mac_address = equipment['mac_address'],
  serial_number = equipment['serial_number'], manufacturer = equipment['manufacturer'],
  date_purchased = equipment['date_purchased'], usage_fee = equipment['usage_fee'],
  active = equipment['active'], last_inspection = equipment['last_inspection'], function = equipment['function'] %}
  {% include "equipment/form.js"%}
{% endwith %}

$('.equipment.modal.header').html("Edit your equipment!");
{% set lab_id = equipment['lab_id']|string %}
$('#equipment_lab_id').dropdown('set selected', {{lab_id}});
