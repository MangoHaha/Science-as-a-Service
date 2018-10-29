$("#instruction_{{sequence}}_approve").html(`{% include 'instruction/approve/unapprove.html' %}`)
$("#sequence-{{sequence}}-edit").addClass("disabled");
var approvable = ("{{order_approvable}}" === "True");
if (approvable) {
  $("#approve_order_button").removeClass("disabled");
} else {
  $("#approve_order_button").addClass("disabled");
}
