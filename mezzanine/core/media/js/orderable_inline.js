
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
                if ($(field).attr('dirty')) {return true;}
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

    var grappelli = !!$('#bookmarks');
    var parentSelector = grappelli ? 'div.items' : 'tbody';

    // Apply drag and drop to orderable inlines.
    $(parentSelector).sortable({handle: '.ordering', axis: 'y', opacity: '.7'});
    $(parentSelector).disableSelection();
    
    // Mark checkboxes with a 'dirty' attribute if they're changed from 
    // their original state, in order to check inside anyFieldsDirty().
    $('input:checkbox').change(function() {
        var checkbox = $(this);
        checkbox.attr('dirty', !checkbox.attr('dirty'));
    });
    
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


