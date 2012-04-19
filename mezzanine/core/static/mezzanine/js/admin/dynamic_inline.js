
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
            case 'file':
                if (field.value) {return true;}
                break;
            case 'checkbox':
                if ($(field).attr('dirty')) {return true;}
                break;
            case 'hidden':
                return false;
            default:
                alert('Unhandled field in orderable_inline.js:' +
                      field.name + ':' + field.type);
        }
        return false;
    });
    return dirty.length > 0;
}

$(function() {

    var itemSelector = window.__grappelli_installed ? '.items' : 'tbody';
    var parentSelector = '.dynamic-inline ' + itemSelector;

    // Apply drag and drop to orderable inlines.
    $(parentSelector).sortable({handle: '.ordering', axis: 'y', opacity: '.7',
                                placeholder: 'placeholder'});
    $(parentSelector + ' .order').disableSelection();
    $('.ordering').css({cursor: 'move'});


    // Mark checkboxes with a 'dirty' attribute if they're changed from
    // their original state, in order to check inside anyFieldsDirty().
    $('input:checkbox').change(function() {
        var checkbox = $(this);
        checkbox.attr('dirty', !checkbox.attr('dirty'));
    });

    // Set the value of the _order fields on submit.
    $('input[type=submit]').click(function() {
        console.log('clicked');
        $.each($(parentSelector), function(i, parent) {
            var order = 0;
            $.each($(parent).find('._order input'), function(i, field) {
                var parent = $(field).parent().parent();
                if (window.__grappelli_installed) {
                    parent = parent.parent();
                }
                if (field.value.length > 0 || anyFieldsDirty(parent.find('input, select, textarea'))) {
                    field.value = order;
                    order += 1;
                } else {
                    field.value = '';
                }
            });
        });
    });

    // Hide the exta inlines.
    $(parentSelector + ' > *:not(.has_original)').hide();
    // Re-show inlines with errors, poetentially hidden by previous line.
    var errors = $(parentSelector + ' ul[class=errorlist]').parent().parent();
    if (window.__grappelli_installed) {
        errors = errors.parent();
    }
    errors.show();

    // Show a new inline when the 'Add another' link is clicked.
    var addAnother = $('.dynamic-inline .add-another a');
    $(addAnother).click(function() {
        var button = $(this);
        var getRows = function() {
            return button.parent().parent().find(itemSelector +' > *:hidden');
        };
        var rows = getRows();
        $(rows[0]).show();
        // Grappelli's inline header for tabular inlines is
        // actually part of the selector, so for it we run this twice.
        if (window.__grappelli_installed && $(rows[0]).hasClass('legend')) {
            $(rows[1]).show();
        }
        if (getRows().length == 0) {
            $(this).hide();
        }
        return false;
    });

    // Show the first hidden inline
    addAnother.click();

});
