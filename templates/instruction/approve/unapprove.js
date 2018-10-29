$("#instruction_{{sequence}}_approve").html(`{% include 'instruction/approve/approve.html' %}`)
$("#sequence-{{sequence}}-edit").removeClass("disabled");
var approvable = ("{{order_approvable}}" === "True");
if (approvable) {
  $("#approve_order_button").removeClass("disabled");
} else {
  $("#approve_order_button").addClass("disabled");
}
