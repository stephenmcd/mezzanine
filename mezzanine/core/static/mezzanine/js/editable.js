jQuery(function($) {

    $(window.__toolbar_html).appendTo('body');

    var iconOpen = '&#8677;', iconClose = '&#8676;';
    var cookieName = 'mezzanine-admin-toolbar';
    var cookieValue = '1';
    var toolbar = $('#editable-toolbar');
    var toolbarToggleButton = $('#editable-toolbar-toggle');
    var toolbarElements = toolbar.find('*[id!=editable-toolbar-toggle]');
    var links = $('.editable-link');

    // Add AJAX submit handler for each editable form.
    $('.editable-form').submit(function() {
        var form = $(this);
        var loading = $('#editable-loading');
        var win = $(window);
        var showError = function(msg) {
            alert('An error occurred' + (msg ? ': ' + msg : ''));
            loading.hide();
            form.show();
        };
        loading.css({
            top: (win.height() - loading.height()) / 2 + win.scrollTop() + "px",
            left: (win.width() - loading.width()) / 2 + win.scrollLeft() + "px"
        });
        form.hide();
        loading.show();
        if (typeof tinyMCE != "undefined" ) {
            tinyMCE.triggerSave();
        }
        form.ajaxSubmit({success: function(data) {
            if (data && data != '<head></head><body></body>') {
                showError(data);
            } else {
                location.reload();
            }
        }, error: function() {
            showError();
        }});
        return false;
    })

    // Iterate through each of the editable areas and set them up:
    //  - position the editable area's edit link
    //  - apply the editable area's overlay handler
    //  - position the editable area's highlight
    $.each($('.editable-original'), function(i, editable) {
        editable = $(editable);
        var link = editable.next('.editable-link');
        link.offset({
            top: editable.offset().top,
            left: editable.offset().left - link.outerWidth() - 5
        }).overlay({
            expose: {color: '#333', loadSpeed: 200, opacity: 0.9},
            closeOnClick: true, close: ':button',
            left: 'center', top: 'center'
        });
        link.next('.editable-highlight').css({
            width: editable.width(),
            height: editable.height()
        }).offset({
            top: editable.offset().top, left: editable.offset().left
        });
    });

    // Show/hide the editable area's highlight when mousing over/out the of
    // the edit link.
    links.hover(function(e) {
        $(this).next('.editable-highlight').css('visibility', 'visible');
    }, function(e) {
        $(this).next('.editable-highlight').css('visibility', 'hidden');
    });

    // Get the toolbar state from cookie, returns null if never set.
    var toolbarOpen = function() {
        var at = ('; ' + document.cookie).indexOf('; ' + cookieName + '=');
        if (at > -1) {
            at += cookieName.length + 1
            return document.cookie.substr(at).split(';')[0] == cookieValue;
        }
        return null;
    };

    // Shows/hides the toolbar, also setting the cookie state.
    var toggleToolbar = function(hide) {
        if (hide) {
            toolbarToggleButton.html(iconOpen);
            toolbarElements.hide();
            links.css('visibility', 'hidden');
            document.cookie = cookieName + '=' + cookieValue + '; path=/';
        } else {
            toolbarToggleButton.html(iconClose);
            toolbarElements.show();
            links.css('visibility', 'visible');
            document.cookie = cookieName + '=; path=/';
        }
    };

    toolbar.fadeIn('slow');
    toggleToolbar(toolbarOpen() != false);  // null first time, start closed.
    toolbarToggleButton.click(function() {
        toggleToolbar(!toolbarOpen());
        return false;
    });

});
