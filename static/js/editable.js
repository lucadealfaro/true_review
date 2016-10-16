jQuery(document).ready(function() {
    var editables = $("span.editable");
    for (var i = 0; i < editables.length; i++) {
        var el = $(editables[i]);
        el.editable("click", function(e) {
            ajax_update(e);
        });
    }
    var areas_editable = $("p.editable");
    var areas_option = {type : "textarea", action : "click"};
    for (var i = 0; i < areas_editable.length; i++) {
        var el = $(areas_editable[i]);
        el.editable(areas_option, function(e) {
            ajax_update(e);
        })
    }
});

function ajax_update(e) {
    if (e.value !== e.old_value) {
        var msg = 'msg=' + JSON.stringify({
                'info': e.target.attr('data_info'),
                'value': e.value
            });
        var icon = e.target.siblings("i.fa");
        // Draws the spinning spinner.
        icon.removeClass("fa-exclamation-circle")
            .addClass("fa-spinner").addClass("fa-pulse");
        icon.show();
        jQuery.post(e.target.attr('data_url'), msg, function(data) {
            // Removes spinner.
            if (data['valid'] === true) {
                icon.removeClass("fa-pulse");
                icon.hide();
            } else {
                // We show the error icon.
                icon.removeClass("fa-pulse").removeClass("fa-spinner")
                    .addClass("fa-exclamation-circle");
                icon.fadeOut(5000);
                e.target.html(e.old_value);
            }
        }, 'json');
    }
}
