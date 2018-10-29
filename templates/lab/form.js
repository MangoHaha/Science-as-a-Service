$('.lab.modal.content').html(`{%- include 'lab/form.html' -%}`);

$('.lab.modal.actions').html(`{%- include 'lab/form_action.html' -%}`);

$('.ui.checkbox').checkbox();

//Semantic UI validations
$('#lab-dialog').modal({
  setting : { transition: 'horizontal flip' },
  onApprove : function() {
    $('.ui.lab.form').form('validate form');
    return false;
  }
});

$('.ui.lab.form').form({
  fields: {
    name: {
      identifier: 'lab[name]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter a name for this lab'
        }
      ]
    },
    address: {
      identifier: 'lab[address]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter an address for this lab'
        }
      ]
    },
    usage_fee: {
      identifier: 'lab[usage_fee]',
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
    area: {
      identifier  : 'lab[area]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter an area'
        },
        {
          type   : 'integer[1..100000]',
          prompt : 'Please enter an integer value less than 100,000'
        }
      ]
    },
    safety_level: {
      identifier  : 'lab[safety_level]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter a safety level'
        },
        {
          type   : 'integer[1..3]',
          prompt : 'Please enter an integer value between 1 and 3'
        }
      ]
    }
  },
  inline: true,
  onSuccess: function() {
    console.log("onSuccess was called!");
    $('.ui.ok.lab.button').addClass("disabled");
    submitForm()
  }
});


function submitForm() {
  console.log("submitForm called");
  // get the form data
  // there are many ways to get this data using jQuery (you can use the class or id also)
  var form = $('#lab-form')[0];
  console.log(form);
  var data = new FormData(form);
  console.log(data);
  // process the form
  $.ajax({
      type        : '{{method}}', // method define the type of HTTP verb we want to use (POST/PATCH for our form)
      url         : $('#lab-form').attr('route'), // the url where we want to POST
      data        : data,// our data object
      contentType : false,
      processData : false,
      // headers     : { "X-CSRF-TOKEN": $('input[name="_csrf_token"]').val() },
      dataType    : 'script', // what type of data do we expect back from the server
      encode      : true

  })
      // using the done promise callback
      .done(function(data) {

        $('.ui.ok.lab.button').removeClass("disabled");
          // log data to the console so we can see
          console.log(data);

          // here we will handle errors and validation messages
      });

  // stop the form from submitting the normal way and refreshing the page
  return false
};
