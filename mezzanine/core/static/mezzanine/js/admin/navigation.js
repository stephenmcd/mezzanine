
// Global flag used for checking whether to hide the visible menu after a small
// timeout has passed when mousing out from a menu.
var onMenu;

$(function() {

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', window.__csrf_token);
        }
    });

    // Empty out the breadcrumbs div and position the menu over it.
    var breadcrumb = $('.breadcrumbs');
    $('.breadcrumbs').html(' ').show();
    $('body').append($('.dropdown-menu'));
    // The top value here previously used breadcrumb.offset().top but breaks
    // when scrolling and reloading in Firefox, so to resolve this it's
    // hard-coded for now. Reported in github issue #11
    var menuCss;
    if (window.__grappelli_installed) {
        menuCss = {top: 30, position: 'fixed'};
    } else {
        menuCss = {top: 37, position: 'absolute'};
        $('.change-form').css({marginBottom: '30px'});
    }
    $('.dropdown-menu').css(menuCss).show();

    $('.dropdown-menu a').mouseover(function() {
        var parent = $(this).parent();
        var menu = parent.find('.dropdown-menu-menu').clone();
        // If we're over a primary menu link, clone the child menu and show it.
        if (menu.length == 1) {
            onMenu = true;
            $('.cloned').remove();
            $('body').append(menu);
            // Position the child menu under its parent.
            var pos = {
                top: breadcrumb.offset().top + breadcrumb.height(),
                left: parent.offset().left,
                position: 'absolute'
            }
            menu.css(pos).addClass('cloned').show();
            // Ensure the menu stays visible when we mouse onto another item in it.
            menu.mouseover(function() {
                onMenu = true;
            });
            // Trigger the parent mouseout if we mouseout of the menu.
            menu.mouseout(function() {
                $('.dropdown-menu a').mouseout();
            });
        }
    });

    // Set a timeout to hide visible menus on mouseout of primary menu item.
    $('.dropdown-menu a').mouseout(function() {
        var parent = $(this).parent();
        if (parent.find('.dropdown-menu-menu').length == 1) {
            onMenu = false;
            window.setTimeout(function() {
                if (!onMenu) {
                    $('.cloned').remove();
                }
            }, 1000);
        }
    })

    // Provides link back to homepage.
    $('#user-tools li:last').before('<li><a href="/">View Site</a></li>');

});

// Remove extraneous ``template`` forms from inline formsets since
// Mezzanine has its own method of dynamic inlines.
$(function() {
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
});
