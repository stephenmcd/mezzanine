
/*
Attach behaviour to the keywords field so that a textbox can be used rather 
than the default select-multiple for ManyToMany fields.
*/

$(function() {

    // Hide the select-multiple for the keywords field and add a textbox beside 
    // it with a comma separated list of existing keywords selected in the 
    // select-multiple.
    $('#id_keywords, #add_id_keywords, .keywords p.help').hide();
    var keywords = $.map($('#id_keywords option:selected'), function(option) {
        return option.text;
    });
    var width = $('textarea:first').width() + 'px';
    $('#id_keywords').before('<input id="text_keywords" name="text_keywords" ' +
        'type="text" value="' + keywords.join(', ') + '" style="width:' +
        width + '; margin-bottom:5px;" />');
    
    // Add an anchor for each keyword that allows the user to add or remove 
    // tags by clicking the keyword's anchor.
    $('#id_keywords').after('<p id="keyword_anchors" style="margin-left:' +
        $('fieldset label').width() + 'px; width:' + width + ';"></p>');
    $.each($('#id_keywords option'), function(i, option) {
        $('#keyword_anchors').append('<a style="float:left;margin-left:10px;" ' +
            'href="#">' + ($.inArray(option.text, keywords) >= 0 ? '-' : '+') + 
            option.text + '</a>');
    });
    $('#keyword_anchors a').click(function() {
        var field = $('#text_keywords');
        var keywords = $.map(field.attr('value').split(','), function(keyword) {
            return $.trim(keyword);
        });
        var keywords = $.grep(keywords, function(keyword) {
            return keyword.length > 0;
        });
        var op, keyword = $(this).text().substr(1);
        if ($.inArray(keyword, keywords) >= 0) {
            keywords = $.grep(keywords, function(keep) {
                return keep != keyword;
            });
            op = '+';
        } else {
            keywords[keywords.length] = keyword;
            op = '-';
        }
        field.attr('value', keywords.join(', '))
        $(this).text(op + keyword);
        return false;
    });

    // On submit of the form, post the keywords from the textbox to the AJAX 
    // URL that will create the keywords if required, and return their IDs. 
    // Then add the IDs as selected items to the previously hidden 
    // select-multiple, and allow form to submit.
    var keywordsSaved = false;
    var form = $('#id_keywords').attr('form');
    $(form).submit(function() {
        if (!keywordsSaved) {
            var keywords = {text_keywords: form.text_keywords.value};
	        $.post('/admin_keywords_submit/', keywords, function(ids) {
	            $('#id_keywords').html('');
    	        if (ids.length > 0) {
	                $('#id_keywords').html($.map(ids.split(','), function(id) {
	                    return '<option selected value="' + id + '"></option>';
	                }).join(''));
	            }
	            keywordsSaved = true;
	            form.submit();
	        });
        }
        return keywordsSaved;
    });

});
