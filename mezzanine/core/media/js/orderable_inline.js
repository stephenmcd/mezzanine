
var anyFieldsDirty = function(fields) {
    // Return true if any of the given fields have been given a value.
    var dirty = $.grep(fields, function(field) {
        switch (field.type) {
            case 'select-one':
                if (field.selectedIndex > 0) {return true;}
                break;
            case 'select-multiple':
                if (field.selectedIndex > -1) {return true;}
                break;
            case 'text':
            case 'textarea':
                if (field.value) {return true;}
                break;
            case 'checkbox':
                if (field.checked) {return true;}
                break;
            default:
                alert('Unhandled field in orderable_inline.js:' +
                    field.name + ':' + field.type);
        }
        return false;
    });
    return dirty.length > 0;
}

$(function() {

    var parentSelector = 'div.items'; // grappelli
    var grappelli = $(parentSelector).length > 0;
    if (!grappelli) {
        parentSelector = 'tbody';
    }

    // Apply drag and drop to orderable inlines.
    $(parentSelector).sortable({handle: '.ordering', axis: 'y', opacity: '.7'});
    $(parentSelector).disableSelection();

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
    parent.append('<p class="add-another">' +
        '<img src="' + $('.ordering:first img:first').attr('src').replace(
        'arrow-up', 'icon_addlink') + '" /><a href="#">Add another</a></p>');
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
    
    // Set the value of the _order fields on submit.
    $($('._order input:first').attr('form')).submit(function() {
        $.each($(parentSelector), function(i, parent) {
            var order = 0;
            $.each($(parent).find('._order input'), function(i, field) {
                field.value = '';
                var fields = $(field).parent().parent().find(
                        'input:not(:hidden), select, textarea');
                if (anyFieldsDirty(fields)) {
                    field.value = order;
                    order += 1;
                } else {
                    field.value = '';
                }
            });
        });
    });

});


