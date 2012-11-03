$(function() {
    var close = 'img';
    var expose = {color: '#333', loadSpeed: 0, closeSpeed: 0, opacity: 0.9};
    var overlay = {
        expose: expose,
        close: close,
        onLoad: function() {$('.image-overlay').expose(expose);}
    }
    $('.gallery a[rel]').overlay(overlay).click(function() {
        location = $(this).attr('rel') + '-show';
    });
    $('.image-overlay-prev, .image-overlay-next').click(function() {
        var dir = $(this).attr('class').replace('image-overlay-', '');
        var to = $(this).parent().parent()[dir]();
        if (to.length == 0) {
            to = $('.gallery li:' + {prev: 'last', next: 'first'}[dir]);
        }
        $(this).parent().find(close).click();
        to.find('a:first').click();
        return false;
    });
    $('body').click(function(e) {
        var ignore = ['image-overlay-thumb', 'image-overlay-full', 'thumbnail'];
        var target = $(e.target);
        if ($.grep(ignore, function(name) {return target.hasClass(name)}).length == 0) {
            $('.image-overlay img:visible').click();
            location = '#';
        }
    });
    if (location.hash.indexOf('#image-') == 0) {
        $('a[rel=' + location.hash.replace('-show', '') + ']').click();
    }
});
