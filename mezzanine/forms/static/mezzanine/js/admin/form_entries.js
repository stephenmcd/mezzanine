
jQuery(function($) {
    // Show the filter criteria fields when a filter option is selected.
    $('.filter select').change(function() {
        var filtering = this.selectedIndex > 0;
        var options = $(this).parent().parent().find('.options-div');
        options.css({visibility: filtering ? 'visible' : 'hidden'});
        // Focus the first field.
        if (filtering) {
            var input = options.find('input:first');
            if (input.length == 1) {
                input.focus();
            } else {
                options.find('select:first').focus();
            }
        }
    }).change();
    // Toggle the include `All` checkboxes - grouped within table tags.
    $('#content-main table').each(function(i, table) {
        table = $(table);
        var all = table.find(':checkbox.include-all');
        var others = table.find('.include :checkbox');
        others.change(function() {
            all.attr('checked', table.find('.include :checkbox:not(:checked)').length == 0);
        });
        all.change(function() {
            others.attr('checked', !!all.attr('checked'));
        });
    });
    // Add a confirmation prompt for deleting entries.
    $('input[name="delete"]').click(function() {
        if ($('input[name="selected"]:checked').length == 0) {
            alert(gettext('No entries selected'));
            return false;
        } else {
            return confirm(gettext('Delete selected entries?'));
        }
    });
});
