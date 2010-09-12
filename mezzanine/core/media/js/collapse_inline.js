
$(function() {

    var grappelli = !!$('#bookmarks');
    var parentSelector = grappelli ? 'div.items' : 'tbody';

    // Hide the exta inlines.
    $(parentSelector + ' > *:not(.has_original)').hide();
    // Re-show inlines with errors, poetentially hidden by previous line.
    var errors = $(parentSelector + ' ul[class=errorlist]').parent().parent();
    if (grappelli) {
        errors = errors.parent();
    }
    errors.show();
    
    // Add the 'Add another' link to the end of the inlines.
    var parent = $(parentSelector).parent();
    if (!grappelli) {
        parent = parent.parent();
    }
    parent.append('<p class="add-another"><a href="#">Add another</a></p>');
    $('.add-another').click(function() {
        // Show a new inline when the 'Add another' link is clicked.
        var rows = $(this).parent().find(parentSelector + ' > *:hidden');
        $(rows[0]).show();
        if (rows.length == 1) {
            $(this).hide();
        }
        return false;
    });
    // Show the first hidden inline - grappelli's inline header is actually
    // part of the selector so for it we run this twice.
    $('.add-another').click();
    if (grappelli) {
        $('.add-another').click();
    }

});


