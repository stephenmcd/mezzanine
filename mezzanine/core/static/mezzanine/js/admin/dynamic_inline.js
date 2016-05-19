
jQuery(function($) {

    var selectFieldDirty = function(select, unselectedIndex) {
        return $.grep(select.options, function(option) {
            return option.selected && !option.defaultSelected;
        }).length > 0 && select.selectedIndex != unselectedIndex;
    };

    var anyFieldsDirty = function(fields) {
        // Return true if any of the fields have been given a value
        // that isn't the default.
        return $.grep(fields, function(field) {
            switch (field.type) {
                case 'select-one':
                    return selectFieldDirty(field, 0);
                case 'select-multiple':
                    return selectFieldDirty(field, -1);
                case 'text':
                case 'textarea':
                case 'file':
                case 'email':
                case 'number':
                case 'password':
                case 'url':
                    return field.value && field.value != field.defaultValue;
                case 'checkbox':
                    return field.checked != field.defaultChecked;
                case 'hidden':
                    return false;
                default:
                    alert('Unhandled field in dynamic_inline.js:' +
                          field.name + ':' + field.type);
                    return false;
            }
        }).length > 0;
    };

    var itemSelector = window.__grappelli_installed ? '.items' : 'tbody';
    var parentSelector = '.inline-group ' + itemSelector;
    var orderSelector = '._order input, .field-_order input';

    // Apply drag and drop to orderable inlines.
    $(parentSelector).sortable({handle: '.ordering', axis: 'y', opacity: '.7',
                                placeholder: 'placeholder'});
    $(parentSelector + ' .order').disableSelection();
    $('.ordering').css({cursor: 'move'});

    // Set the value of the _order fields on submit.
    $('.inline-group').closest("form").submit(function() {
        // Try to save TinyMCE instances (in case there are some in the inlines)
        if (typeof tinyMCE != 'undefined') {
            try {
                tinyMCE.triggerSave();
            } catch (e) {
                console.log("TinyMCE error:", e);
            }
        }
        $.each($(parentSelector), function(i, parent) {
            var order = 0;
            $.each($(parent).find(orderSelector), function(i, field) {
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
});
