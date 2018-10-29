$('#equipment-dialog').modal( {observeChanges: true}).modal("show");

{% with method='POST', route='/equipment' %}
{% include "equipment/form.js"%}
{% endwith %}

$('.equipment.modal.header').html("Add a new piece of equipment!");
