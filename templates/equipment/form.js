$('.equipment.modal.content').html(`{%- include 'equipment/form.html' -%}`);

$('.equipment.modal.actions').html(`{%- include 'equipment/form_action.html' -%}`);

$('.ui.checkbox').checkbox();
$('select.dropdown').dropdown();

//Semantic UI validations
$('#equipment-dialog').modal({
  setting : { transition: 'horizontal flip' },
  onApprove : function() {
    $('.ui.equipment.form').form('validate form');
    return false;
  }
});


$('.ui.equipment.form').form({
  fields: {
    lab: {
      identifier: 'equipment[lab_id]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Equipment must be housed in a lab'
        }
      ]
    },
    serial_number: {
      identifier: 'equipment[serial_number]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter the equipment serial number'
        }
      ]
    },
    manufacturer: {
      identifier: 'equipment[manufacturer]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter the equipment manufacturer'
        }
      ]
    },
    mac_address: {
      identifier: 'equipment[mac_address]',
      rules: [
        {
          type   : 'regExp[/^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/]',
          prompt : 'Please enter a mac address'
        }
      ]
    },
    usage_fee: {
      identifier: 'equipment[usage_fee]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter a usage fee amount'
        },
        {
          type   : 'integer[1..100000]',
          prompt : 'Please enter a valid integer amount less than 100,000'
        }
      ]
    },
    purchase_date: {
      identifier: 'equipment[purchase_date]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter a purchase date for this equipment'
        }
      ]
    },
    inspection_date: {
      identifier: 'equipment[last_inspected]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter an inspection date for this equipment'
        }
      ]
    }
  },
  inline: true,
  onSuccess: function() {
    console.log("onSuccess was called!");
    $('.ui.ok.equipment.button').addClass("disabled");
    submitForm()
  }
});


function submitForm() {
  console.log("submitForm called");
  // get the form data
  // there are many ways to get this data using jQuery (you can use the class or id also)
  var form = $('#equipment-form')[0];
  console.log(form);
  var data = new FormData(form);
  console.log(data);
  // process the form
  $.ajax({
      type        : '{{method}}', // method define the type of HTTP verb we want to use (POST/PATCH for our form)
      url         : $('#equipment-form').attr('route'), // the url where we want to POST
      data        : data,// our data object
      contentType : false,
      processData : false,
      // headers     : { "X-CSRF-TOKEN": $('input[name="_csrf_token"]').val() },
      dataType    : 'script', // what type of data do we expect back from the server
      encode      : true

  })
      // using the done promise callback
      .done(function(data) {

        $('.ui.ok.equipment.button').removeClass("disabled");
          // log data to the console so we can see
          console.log(data);

          // here we will handle errors and validation messages
      });

  // stop the form from submitting the normal way and refreshing the page
  return false
};
