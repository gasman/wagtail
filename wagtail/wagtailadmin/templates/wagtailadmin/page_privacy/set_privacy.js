function(modal) {
    $('form', modal.body).submit(function() {
        modal.postForm(this.action, $(this).serialize());
        return false;
    });

    var restrictionTypeField = $("#id_restriction_type", modal.body);
    var passwordRow = $("li.password-field", modal.body);
    var passwordField = $("#id_password", modal.body);
    var groupFields = $("#id_groups input[name='groups']", modal.body);
    var groupsRow = $("li.groups-field", modal.body);
    function refreshFormFields() {
        var restrictionType = restrictionTypeField.val();

        if (restrictionType == "none") {
            passwordField.attr('disabled', true);
            passwordRow.hide();
            groupFields.attr('disabled', true);
            groupsRow.hide();
        } else if (restrictionType == "password") {
            passwordField.removeAttr('disabled');
            passwordRow.show();
            groupFields.attr('disabled', true);
            groupsRow.hide();
        } else if (restrictionType == "group") {
            passwordField.attr('disabled', true);
            passwordRow.hide();
            groupFields.removeAttr('disabled');
            groupsRow.show();
        }
    }
    refreshFormFields();

    restrictionTypeField.change(refreshFormFields);
}
