
jQuery(function($) {

    $('.keywords-field').css(window.__grappelli_installed ?
                            {margin: '5px 0 0 130px', width: '700px'} :
                            {margin: '5px 0 0 75px', width: '620px'} );

    // Add click functionality to each keyword so that it toggles
    // the keyword's existance in the associated input box.
    $('.keywords-field a').click(function() {
        var field = $(this).parent().prev('input[type=text]');
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

    // When submitting the form, go through each of the keywords
    // fields and post their keywords via AJAX, to retrieve a list of
    // keyword IDs for storing in each of the associated hidden fields.
    var keywordsSaved = false;
    $('input[type=submit]').click(function() {
        if (keywordsSaved) {
            return true;
        }
        var button = $(this);
        var fields = $.makeArray($('.keywords-field').prev('input[type=text]'));
        var submitKeywords = function() {
            var field = fields.shift();
            var keywords = {text_keywords: field.value};
            $.post(window.__admin_keywords_submit_url, keywords, function(data) {
                var ids = data.split("|")[0].split(',');
                field.value = data.split("|")[1];
                $(field).prev('input').attr('value', ids);
                if (fields.length > 0) {
                    submitKeywords();
                } else {
                    keywordsSaved = true;
                    button.click();
                }
            });
        };
        submitKeywords();
        return false;
    });

});
