
jQuery(function($) {

    /// FIELDSETS
    $('fieldset.collapse').each(function() {
        $(this).addClass("collapse-open");
        $(this).removeClass("collapse");
    });
    $('fieldset.collapse-closed').each(function() {
        $(this).addClass("collapsed");
        $(this).find('h2:first').addClass("collapse-toggle");
    });
    $('fieldset.collapse-open').each(function() {
        $(this).find('h2:first').addClass("collapse-toggle");
    });
    $('h2.collapse-toggle').bind("click", function(e){
        $(this).parent().toggleClass('collapsed');
        $(this).parent().toggleClass('collapse-closed');
        $(this).parent().toggleClass('collapse-open');
    });

    /// OPEN FIELDSETS WITH ERRORS
    $('fieldset.collapse-closed').children('div[class*="errors"]').each(function(i) {
        $(this).parent().toggleClass("collapsed");
        $(this).parent().toggleClass('collapse-closed');
        $(this).parent().toggleClass('collapse-open');
    });

});
