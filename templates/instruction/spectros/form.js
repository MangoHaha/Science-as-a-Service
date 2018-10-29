$('.instruction.modal.content').html(`{%- include 'instruction/spectros/form.html' -%}`);

$('.instruction.modal.actions').html(`{%- include 'instruction/spectros/form_action.html' -%}`);

$('.ui.checkbox').checkbox();
$('select.dropdown').dropdown();

showSpectroTypeFields()

//Semantic UI validations
$('#instruction-dialog').modal({
  setting : { transition: 'horizontal flip' },
  onApprove : function() {
    $('.ui.instruction.form').form('validate form');
    return false;
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

function showSpectroTypeFields() {
  $('.ui.instruction.form').find('.error').removeClass('error').find('.prompt').remove();
  type = $('.ui.dropdown.spectro.type').dropdown("get value")
  if (type == 'fluorescence') {
    $('div[name=common_fields]')["show"]();
    $('div[name=fluorescence_fields]')["show"]();
    $('div[name=absorbance_fields]')["hide"]();
    $('.ui.instruction.form').form({
      fields: {
        type: {
          identifier  : 'spectros[type]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please select a type'
            }
          ]
        },
        temperature: {
          identifier  : 'spectros[temperature]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter a temperature'
            },
            {
              type   : 'integer[20..120]',
              prompt : 'Please enter an integer between 20 and 120'
            }
          ]
        },
        type: {
          identifier  : 'spectros[sample_id]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please select a sample'
            }
          ]
        },
        num_flashes: {
          identifier  : 'spectros[fluor_num_flashes]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter a number of flashes'
            },
            {
              type   : 'integer[1..100]',
              prompt : 'Please enter a value between 1 and 100'
            }
          ]
        },
        excitation: {
          identifier  : 'spectros[excitation]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter an excitation value'
            },
            {
              type   : 'integer[230..600]',
              prompt : 'Please enter a value between 230 and 600'
            }
          ]
        },
        emission: {
          identifier  : 'spectros[emission]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter an emission value'
            },
            {
              type   : 'integer[330..850]',
              prompt : 'Please enter a value between 330 and 80'
            }
          ]
        },
        gain: {
          identifier  : 'spectros[gain]',
          optional   : true,
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter a gain value'
            },
            {
              type   : 'decimal',
              prompt : 'Please enter a value between 0.002 and 1.000'
            }
          ]
        },
        duration: {
          identifier: 'spectros[duration]',
          optional: true,
          rules: [
            {
              type   : 'regExp[/(^[0-9]{2})(:{1})([0-9]{2})(:{1})([0-9]{2})$/]',
              prompt : 'Please enter a valid time interval in the format HH:MM:SS'
            }
          ]
        },
        shaking_amplitude: {
          identifier: 'spectros[amplitude]',
          depends: 'spectros[orbital]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter an orbital'
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
  } else if (type == 'absorbance') {
    $('div[name=common_fields]')["show"]();
    $('div[name=fluorescence_fields]')["hide"]();
    $('div[name=absorbance_fields]')["show"]();
    $('.ui.instruction.form').form({
      fields: {
        type: {
          identifier  : 'spectros[type]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please select a type'
            }
          ]
        },
        temperature: {
          identifier  : 'spectros[temperature]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter a temperature'
            },
            {
              type   : 'integer[20..120]',
              prompt : 'Please enter an integer between 20 and 120'
            }
          ]
        },
        type: {
          identifier  : 'spectros[sample_id]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please select a sample'
            }
          ]
        },
        wavelength: {
          identifier  : 'spectros[wavelength]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter a wavelength'
            },
            {
              type   : 'integer[300..1000]',
              prompt : 'Please enter a value between 300 and 1000'
            }
          ]
        },
        num_flashes: {
          identifier  : 'spectros[abs_num_flashes]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter a number of flashes'
            },
            {
              type   : 'integer[1..100]',
              prompt : 'Please enter a value between 1 and 100'
            }
          ]
        },
        duration: {
          identifier: 'spectros[duration]',
          optional: true,
          rules: [
            {
              type   : 'regExp[/(^[0-9]{2})(:{1})([0-9]{2})(:{1})([0-9]{2})$/]',
              prompt : 'Please enter a valid time interval in the format HH:MM:SS'
            }
          ]
        },
        shaking_amplitude: {
          identifier: 'spectros[amplitude]',
          depends: 'spectros[orbital]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter an orbital'
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
  } else {
    $('div[name=common_fields]')["hide"]();
    $('div[name=fluorescence_fields]')["hide"]();
    $('div[name=absorbance_fields]')["hide"]();
    $('.ui.instruction.form').form({
      fields: {
        type: {
          identifier  : 'spectros[type]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please select a type'
            }
          ]
        },
        temperature: {
          identifier  : 'spectros[temperature]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter a temperature'
            },
            {
              type   : 'integer[20..120]',
              prompt : 'Please enter an integer between 20 and 120'
            }
          ]
        },
        type: {
          identifier  : 'spectros[sample_id]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please select a sample'
            }
          ]
        },
        duration: {
          identifier: 'spectros[duration]',
          optional: true,
          rules: [
            {
              type   : 'regExp[/(^[0-9]{2})(:{1})([0-9]{2})(:{1})([0-9]{2})$/]',
              prompt : 'Please enter a valid time interval in the format HH:MM:SS'
            }
          ]
        },
        shaking_amplitude: {
          identifier: 'spectros[amplitude]',
          depends: 'spectros[orbital]',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter an orbital'
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
  }
}
