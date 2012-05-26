$(function($) {

    // Add AJAX submit handler for each editable form.
    $('.editable-form').submit(function() {
        var form = $(this);
        var loading = $('#editable-loading');
        var showError = function(msg) {
            if (msg) {
                msg = ': ' + msg;
            } else {
                msg = '';
            }
            alert('An error occurred' + msg);
            loading.hide();
            form.show();
        };
        loading.css({
            top: ($(window).height() - loading.height()) / 2 + $(window).scrollTop() + "px",
            left: ($(window).width() - loading.width()) / 2 + $(window).scrollLeft() + "px"
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

    // Iterate through each of the editable areas and set them up.
    var realign = function() {
        $.each($('.editable-original'), function(i, editable) {
            editable = $(editable);
            // Position the editable area's edit link.
            var link = editable.next('.editable-link');
            link.css({top: editable.offset().top,
                left: editable.offset().left - link.width() - 12});
            // Apply the editable area's overlay handler.
            var expose = {color: '#333', loadSpeed: 200, opacity: 0.9};
            var overlay = {expose: expose, closeOnClick: true, close: ':button'};
            link.overlay(overlay);
            // Position the editable area's highlight.
            link.next('.editable-highlight').css({
                width: editable.width(), height: editable.height(),
                top: editable.offset().top, left: editable.offset().left
            });
        });
    };

	realign();

    // Show/hide the editable area's highlight when mousing over/out the of
    // the edit link.
    $('.editable-link').hover(function(e) {
    	$(this).next('.editable-highlight').show();
    }, function(e) {
    	$(this).next('.editable-highlight').hide();
    });

    $('body, .editable-original').on('resize', function(e) {
    	realign();
    });

    // Add the toolbar HTML and handlers.
    var cookie = 'mezzanine-admin-toolbar';
    var at = ('; ' + document.cookie).indexOf('; ' + cookie + '=');
    var closed = false;
    if (at > -1) {
        closed = document.cookie.substr(at +
            cookie.length + 1).split(';')[0];
    }
    $(window.__toolbar_html).appendTo('body');
    $('#editable-toolbar-toggle').click(function() {
        var toggle = $(this);
        var controls = $('.editable-link, ' +
            '#editable-toolbar *[id!=editable-toolbar-toggle]');
        if (toggle.text() == '<<') {
            toggle.text('>>');
            controls.hide();
            document.cookie = cookie + '=1; path=/';
        } else {
            toggle.text('<<');
            controls.show();
            document.cookie = cookie + '=; path=/';
        }
        return false;
    });
    $('#editable-toolbar-logout').click(function() {
        $('#editable-toolbar').submit();
        return false;
    });

    $('#editable-toolbar').fadeIn('slow');
    if (!closed) {
        $('#editable-toolbar-toggle').click();
    }

});
