/**
 * SimplSale AJAX helpers.
 */

var ZIP_SERVICE_URI = "../zipcode/";

SimplSale = function () {
    var updateSubmit = function (submitButton, required) {
	// Enable the submit button based on whether or not
	// all of the required fields have non-empty values.
	var values = required.map(function () {
	    return jQuery.trim($(this).val());
	});
	submitButton.attr({
	    disabled: (jQuery.inArray('', values) != -1)
	});
    };

    return {
	syncZIP: function (zipField, cityField, stateField) {
	    // Find each field, then attach an onChange handler to
	    // zipField to update cityField and stateField whenever
	    // zipField changes.
	},

	protectSubmit: function () {
	    // Disable form submission until all required fields have
	    // values.
	    var form = $('form#simplsale-form');
	    var submitButton = form.find('input[type=submit]');
	    var required = form.find('.required');
	    var update = function () {
		updateSubmit(submitButton, required);
	    };
	    // Update the Submit button on every value change and
	    // keypress.
	    required.change(update).keyup(update);
	    // Update it now to reflect current state.
	    update();
	    // Disable submit button when it's clicked, and change its
	    // text to "Please Wait..."
	    form.submit(function () {
		submitButton.attr({
		    value: 'Please Wait...',
		    disabled: true
		});
	    });
	}
    };
}();

$(document).ready(function() {
    SimplSale.protectSubmit();
});
