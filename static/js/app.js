$(document).ready(function() {
  $('.ui.dropdown').dropdown();
  $('.menu .item').tab();
  $('.ui.safety-level.rating').rating({ maxRating: 3 });
  $('.ui.safety-level.rating').rating('disable');
  $('.message .close').on('click', function() {
    $(this).closest('.message').transition('fade');
  });

  var loginFormValidationRules =
    {
      fields: {
        username: {
          identifier: 'username',
          rules: [
            {
              type   : 'email',
              prompt : 'Please enter a valid email address'
            }
          ]
        },
        password: {
          identifier : 'password',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter your password'
            }
          ]
        },
        password: {
          identifier  : 'password',
          rules: [
          {
              type   : 'minLength[5]',
              prompt : 'Password is too short'
            }
          ]
        }
      },
      on: 'blur'
    }
  $('.ui.form.login').form(loginFormValidationRules);
});

$(document).on('page:load', function(){
  $('.ui.dropdown').dropdown();
  $('.menu .item').tab();
  $('.ui.safety-level.rating').rating({ maxRating: 3 });
  $('.ui.safety-level.rating').rating('disable');
  $('.message .close').on('click', function() {
    $(this).closest('.message').transition('fade');
  });
});

function jsGet(e) {
  e.preventDefault();
  var href = this.href;
  $.ajax({
    type: 'GET', url: href, dataType: "script",
    success: e => {},
    error: e => { alert("Request Failed"); },
    complete: e => {}
  })
}

function jsDelete(e) {
  e.preventDefault();
  var message = this.getAttribute("data-confirm")
  if(message === null || confirm(message)){
    var href = this.href;
    $.ajax({
      type: 'DELETE', url: href, dataType: "script",
      success: e => {},
      error: e => { alert("Request Failed"); },
      complete: e => {}
    })
  };
}

$(document).on("click", "a[data-js=get]", jsGet);
$(document).on("click", "a[data-js=delete]", jsDelete);
