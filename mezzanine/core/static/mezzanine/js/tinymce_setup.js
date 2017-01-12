(function($) {
    'use strict';

    // Map Django language codes to valid TinyMCE language codes.
    // There's an entry for every TinyMCE language that exists,
    // so if a Django language code isn't here, we can default to en.

    var language_codes = {
        'ar': 'ar',
        'ca': 'ca',
        'cs': 'cs',
        'da': 'da',
        'de': 'de',
        'es': 'es',
        'et': 'et',
        'fa': 'fa',
        'fa-ir': 'fa_IR',
        'fi': 'fi',
        'fr': 'fr_FR',
        'hr-hr': 'hr',
        'hu': 'hu_HU',
        'id-id': 'id',
        'is-is': 'is_IS',
        'it': 'it',
        'ja': 'ja',
        'ko': 'ko_KR',
        'lv': 'lv',
        'nb': 'nb_NO',
        'nl': 'nl',
        'pl': 'pl',
        'pt-br': 'pt_BR',
        'pt-pt': 'pt_PT',
        'ru': 'ru',
        'sk': 'sk',
        'sr': 'sr',
        'sv': 'sv_SE',
        'tr': 'tr',
        'uk': 'uk_UA',
        'vi': 'vi',
        'zh-cn': 'zh_CN',
        'zh-tw': 'zh_TW',
        'zh-hant': 'zh_TW',
        'zh-hans': 'zh_CN'
    };

    function custom_file_browser(field_name, url, type, win) {
        tinyMCE.activeEditor.windowManager.open({
            title: 'Select ' + type + ' to insert',
            file: window.__filebrowser_url + '?pop=5&type=' + type,
            width: 800,
            height: 500,
            resizable: 'yes',
            scrollbars: 'yes',
            inline: 'yes',
            close_previous: 'no'
        }, {
            window: win,
            input: field_name
        });
        return false;
    }

    var tinymce_config = {
        height: '500px',
        language: language_codes[window.__language_code] || 'en',
        plugins: [
            "advlist autolink lists link image charmap print preview anchor",
            "searchreplace visualblocks code fullscreen",
            "insertdatetime media table contextmenu paste"
        ],
        link_list: window.__link_list_url,
        relative_urls: false,
        convert_urls: false,
        menubar: false,
        statusbar: false,
        toolbar: ("insertfile undo redo | styleselect | bold italic | " +
                  "alignleft aligncenter alignright alignjustify | " +
                  "bullist numlist outdent indent | link image table | " +
                  "code fullscreen"),
        file_browser_callback: custom_file_browser,
        content_css: window.__tinymce_css,
        valid_elements: "*[*]"  // Don't strip anything since this is handled by bleach.
    };

    function initialise_richtext_fields($elements) {
        if ($elements && typeof tinyMCE != 'undefined') {
            $elements.tinymce(tinymce_config);
        }
    }

    // Register a handler for Django's formset:added event, to initialise
    // any rich text fields in dynamically added inline forms.
    $(document).on('formset:added', function(e, $row) {
        initialise_richtext_fields($row.find('textarea.mceEditor'));
    });

    // Initialise all existing editor fields, except those with an id
    // containing the string "__prefix__". Those elements are part of the
    // hidden template inline rows used by Django's dynamic inlines, and they
    // shouldn't be initialised as editors.
    $(document).ready(function() {
        initialise_richtext_fields($('textarea.mceEditor').filter(function() {
            return (this.id || '').indexOf('__prefix__') === -1;
        }));
    });

})(window.django ? django.jQuery : jQuery);
