
jQuery(function($) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', window.__csrf_token);
        }
    });
});
