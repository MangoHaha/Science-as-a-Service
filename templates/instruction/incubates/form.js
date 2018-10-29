$('.instruction.modal.content').html(`{%- include 'instruction/incubates/form.html' -%}`);

$('.instruction.modal.actions').html(`{%- include 'instruction/incubates/form_action.html' -%}`);

$('.ui.checkbox').checkbox();
$('select.dropdown').dropdown();

//Semantic UI validations
$('#instruction-dialog').modal({
  setting : { transition: 'horizontal flip' },
  onApprove : function() {
    $('.ui.instruction.form').form('validate form');
    return false;
  }
});


$('.ui.instruction.form').form({
  fields: {
    duration: {
      identifier: 'incubates[duration]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter a duration'
        },
        {
          type   : 'regExp[/(^[0-9]{1})(:{1})([0-9]{2})(:{1})([0-9]{2})$/]',
          prompt : 'Please enter a valid time interval in the format HH:MM:SS'
        }
      ]
    },
    temperature: {
      identifier  : 'incubates[temperature]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter a temperature'
        },
        {
          type   : 'integer[1..120]',
          prompt : 'Please enter a value between 1 and 120'
        }
      ]
    },
    co2_percent: {
      identifier: 'incubates[co2_percent]',
      rules: [
        {
          type   : 'empty',
          prompt : 'Please enter a percent between 0 and 1.00'
        }
      ]
    }
  },
  inline: true,
  onSuccess: function() {
    console.log("onSuccess was called!");
    $('.ui.ok.instruction.button').addClass("disabled");
    submitForm()
  }
});


function submitForm() {
  console.log("submitForm called");
  // get the form data
  // there are many ways to get this data using jQuery (you can use the class or id also)
  var form = $('#instruction-form')[0];
  console.log(form);
  var data = new FormData(form);
  console.log(data);
  // process the form
  $.ajax({
      type        : '{{method}}', // method define the type of HTTP verb we want to use (POST/PATCH for our form)
      url         : $('#instruction-form').attr('route'), // the url where we want to POST
      data        : data,// our data object
      contentType : false,
      processData : false,
      // headers     : { "X-CSRF-TOKEN": $('input[name="_csrf_token"]').val() },
      dataType    : 'script', // what type of data do we expect back from the server
      encode      : true

  })
      // using the done promise callback
      .done(function(data) {

        $('.ui.ok.instruction.button').removeClass("disabled");
          // log data to the console so we can see
          console.log(data);

          // here we will handle errors and validation messages
      });

  // stop the form from submitting the normal way and refreshing the page
  return false
};
