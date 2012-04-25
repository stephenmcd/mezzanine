
// Global flag used for checking whether to hide the visible menu
// after a small timeout has passed when mousing out from a menu.
var onMenu;

$(function() {

    // Empty out the breadcrumbs div and add the menu into it.
    $('.breadcrumbs').html('')
                     .append($('.dropdown-menu').show())
                     .css({display: 'inline-block'});

    var primaryMenuItems = $('.dropdown-menu a');

    primaryMenuItems.mouseover(function() {
        var menu = $(this).parent().find('.dropdown-menu-menu').clone();
        // If we're over a primary menu link, clone the child menu and
        // show it.
        if (menu.length == 1) {
            onMenu = true;
            $('.cloned').remove();
            $('body').append(menu);
            // Position the child menu under its parent.
            var pos = {
                top: $(this).offset().top + $(this).height(),
                left: $(this).offset().left,
                position: 'absolute'
            }
            menu.css(pos).addClass('cloned').show();
            // Ensure the menu stays visible when we mouse onto
            // another item in it.
            menu.mouseover(function() {
                onMenu = true;
            });
            // Trigger the parent mouseout if we mouseout of the menu.
            menu.mouseout(function() {
                $('.dropdown-menu a').mouseout();
            });
        }
    });

    // Set a timeout to hide visible menus on mouseout of primary
    // menu item.
    primaryMenuItems.mouseout(function() {
        if ($(this).parent().find('.dropdown-menu-menu').length == 1) {
            onMenu = false;
            window.setTimeout(function() {
                if (!onMenu) {
                    $('.cloned').remove();
                }
            }, 1000);
        }
    });

     // If the primary menu item is clicked, go to the URL for
     // its first child.
     primaryMenuItems.click(function() {
        var thisHref = $(this).attr('href');
        if (thisHref && thisHref != '#') {
            return true;
        }
        var first = $(this).parent().find('.dropdown-menu-menu a:first');
        var firstHref = first.attr('href');
        if (firstHref) {
            location = firstHref;
        }
        return false;
    });

    // Give the drop-down menu items elements the same hover
    // state and click event as their anchors.
    var subMenuItems = $('.dropdown-menu-menu li');

    subMenuItems.live('mouseover', function() {
        $(this).addClass('dropdown-menu-hover');
    });

    subMenuItems.live('mouseout', function() {
        $(this).removeClass('dropdown-menu-hover');
    });

    subMenuItems.live('click', function() {
        location = $(this).find('a').attr('href');
    });

    // Provides link to site.
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
