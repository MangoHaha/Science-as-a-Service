$('#lab-dialog').modal( {observeChanges: true}).modal("show");

{% with method='POST', route='/labs' %}
{% include "lab/form.js"%}
{% endwith %}

$('.lab.modal.header').html("Make a lab!");
