
jQuery(function($) {

    // Empty out the breadcrumbs div and add the menu into it.
    $('body').prepend($('.dropdown-menu'));
    $('body').prepend($('.messagelist'));

    // Set the hrefs for the primary menu items to the href of their first
    // child (unless the primary menu item already has an href).
    $('.dropdown-menu a').each(function() {
       if ( $(this).attr('href') == '#' ) {
         $(this).attr('href', $(this).parent().find('.dropdown-menu-menu a:first').attr('href'));
       }
    });

    // Provides link to site.
    $('#user-tools li:last').before('<li>' + window.__home_link + '</li>');

    // Fixes issue #594 but is incomplete, see #677

    // function contentMargin() {
    //     // Set margin on main content area so it clears all the fixed-position elements above it
    //     var clearedHeight = 21;
    //     $('#content').prevAll().each(function() {
    //         clearedHeight += $(this).height();
    //     });

    //     $('#content').css('margin-top', clearedHeight);
    // }

    // // Check that content clears menus on both load and resize
    // contentMargin();
    // $(window).resize(contentMargin);

    // Remove extraneous ``template`` forms from inline formsets since
    // Mezzanine has its own method of dynamic inlines.
    var removeRows = {};
    $.each($('*[name*=__prefix__]'), function(i, e) {
        var row = $(e).parent();
        if (!row.attr('id')) {
            row.attr('id', 'remove__prefix__' + i);
        }
        removeRows[row.attr('id')] = true;
    });
    for (var rowID in removeRows) {
        $('#' + rowID).remove();
    }

    // SIDE NAV
    var cur_menu, grandparent;

    // hide all dropdown menus
    $('.dropdown-menu-menu').removeClass('open').hide();

    // on li click see if the li contains a dropdown-menu-menu and open it
    $('.dropdown-menu > ul > li').click(function(){
        cur_menu = $(this).children('.dropdown-menu-menu');
        if (cur_menu.length > 0){
            if (!cur_menu.hasClass('open')) {
                $('.dropdown-menu-menu').removeClass('open').hide(400);
                cur_menu.show(400).addClass('open');
                return false;
            }
        }
    });

    // open the menu corresopnding to the current path
    $('.dropdown-menu ul li > a').each(function() {
        if (~window.location.pathname.indexOf($(this).attr('href'))) {
            grandparent = $(this).parent().parent();
            if (grandparent.hasClass('dropdown-menu-menu')) {
                grandparent.addClass('open').show();
            } else {
                $(this).addClass('open').show();
            }
        }
    });
});
