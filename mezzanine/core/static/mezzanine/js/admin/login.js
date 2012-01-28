$(function() {
    // We "inject" the extra login fields here rather than defining them in the
    // login.html template, since we don't want to override the login.html
    // template as it's very different between Grappelli and the regular admin.
    if ($('#id_password').length == 1) {
        $('#forgot-password').insertAfter($('.submit-row')).show();
        $('#extra-login-fields').insertAfter($('#id_password').parent()).show();
    }
    // Fix the ``Home`` breadcrumb link non logged-in views.
    var home = $('.breadcrumbs a:first');
    if (home.length == 1) {
        home.attr('href', window.__admin_url);
    }
    // Fix the submit margin on the new password form.
    if ($('#id_new_password1').length == 1) {
        $('input:submit').css({marginTop: '20px'});
    }
});
