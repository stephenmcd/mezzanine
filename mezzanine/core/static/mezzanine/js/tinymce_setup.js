
// Map Django language codes to valid TinyMCE language codes.
// There's an entry for every TinyMCE language that exists,
// so if a Django language code isn't here, we can default to en.
// Rather than assuming the language codes map perfectly between
// Django and TinyMCE, we map them here so that they can be
// tweaked - they've not yet all been verified to be correct.

var language_codes = {
    'ar': 'ar',
    'az': 'az',
    'be': 'be',
    'bg': 'bg',
    'bn': 'bn',
    'br': 'br',
    'bs': 'bs',
    'ca': 'ca',
    'ch': 'ch',
    'cn': 'cn',
    'cs': 'cs',
    'ct': 'ct',
    'cy': 'cy',
    'da': 'da',
    'de': 'de',
    'dv': 'dv',
    'el': 'el',
    'en': 'en',
    'eo': 'eo',
    'es': 'es',
    'et': 'et',
    'eu': 'eu',
    'fa': 'fa',
    'fi': 'fi',
    'fr': 'fr',
    'gl': 'gl',
    'gu': 'gu',
    'he': 'he',
    'hi': 'hi',
    'hr': 'hr',
    'hu': 'hu',
    'hy': 'hy',
    'ia': 'ia',
    'id': 'id',
    'is': 'is',
    'it': 'it',
    'ja': 'ja',
    'ka': 'ka',
    'kb': 'kb',
    'kk': 'kk',
    'kl': 'kl',
    'km': 'km',
    'ko': 'ko',
    'lb': 'lb',
    'lt': 'lt',
    'lv': 'lv',
    'mk': 'mk',
    'ml': 'ml',
    'mn': 'mn',
    'ms': 'ms',
    'my': 'my',
    'nb': 'nb',
    'nl': 'nl',
    'nn': 'nn',
    'no': 'no',
    'pl': 'pl',
    'ps': 'ps',
    'pt': 'pt',
    'ro': 'ro',
    'ru': 'ru',
    'sc': 'sc',
    'se': 'se',
    'si': 'si',
    'sk': 'sk',
    'sl': 'sl',
    'sq': 'sq',
    'sr': 'sr',
    'sv': 'sv',
    'sy': 'sy',
    'ta': 'ta',
    'te': 'te',
    'th': 'th',
    'tn': 'tn',
    'tr': 'tr',
    'tt': 'tt',
    'tw': 'tw',
    'uk': 'uk',
    'ur': 'ur',
    'vi': 'vi',
    'zh-cn': 'zh-cn',
    'zh-tw': 'zh-tw',
    'zh': 'zh',
    'zu': 'zu'
};

function CustomFileBrowser(field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({
        file: window.__filebrowser_url + '?pop=2&type=' + type,
        width: 820,  // Your dimensions may differ - toy around with them!
        height: 500,
        resizable: "yes",
        scrollbars: "yes",
        inline: "yes",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: "no"
    }, {
        window: win,
        input: field_name,
        editor_id: tinyMCE.selectedInstance.editorId
    });
    return false;
}

jQuery(function($) {

    if (typeof tinyMCE != 'undefined') {

        tinyMCE.init({

            // main settings
            mode : "specific_textareas",
            editor_selector : "mceEditor",
            theme: "advanced",
            language: language_codes[window.__language_code] || 'en',
            dialog_type: "window",
            editor_deselector : "mceNoEditor",
            skin: "thebigreason",

            // general settings
            width: '800px',
            height: '450px',
            indentation : '10px',
            fix_list_elements : true,
            remove_script_host : true,
            accessibility_warnings : false,
            object_resizing: false,
            //cleanup: false, // SETTING THIS TO FALSE WILL BREAK EMBEDDING YOUTUBE VIDEOS
            forced_root_block: "p",
            remove_trailing_nbsp: true,

            external_link_list_url: '/displayable_links.js',
            relative_urls: false,
            convert_urls: false,

            // enable browser's built in spell checking
            gecko_spellcheck: true,

            // callbackss
            file_browser_callback: "CustomFileBrowser",

            // theme_advanced
            theme_advanced_toolbar_location: "top",
            theme_advanced_toolbar_align: "left",
            theme_advanced_statusbar_location: "",
            theme_advanced_buttons1: "bold,italic,|,link,unlink,|,image,|,media,charmap,|,code,|,table,|,bullist,numlist,blockquote,|,undo,redo,|,formatselect,|,search,replace,|,fullscreen,",
            theme_advanced_buttons2: "",
            theme_advanced_buttons3: "",
            theme_advanced_path: false,
            theme_advanced_blockformats: "p,h1,h2,h3,h4,pre",
            theme_advanced_styles: "[all] clearfix=clearfix;[p] small=small;[img] Image left-aligned=img_left;[img] Image left-aligned (nospace)=img_left_nospacetop;[img] Image right-aligned=img_right;[img] Image right-aligned (nospace)=img_right_nospacetop;[img] Image Block=img_block;[img] Image Block (nospace)=img_block_nospacetop;[div] column span-2=column span-2;[div] column span-4=column span-4;[div] column span-8=column span-8",
            theme_advanced_resizing : true,
            theme_advanced_resize_horizontal : false,
            theme_advanced_resizing_use_cookie : true,
            theme_advanced_styles: "Image left-aligned=img_left;Image left-aligned (nospace)=img_left_nospacetop;Image right-aligned=img_right;Image right-aligned (nospace)=img_right_nospacetop;Image Block=img_block",
            advlink_styles: "intern=internal;extern=external",

            // plugins
            plugins: "inlinepopups,contextmenu,tabfocus,searchreplace,fullscreen,advimage,advlink,paste,media,table",
            advimage_update_dimensions_onchange: true,

            // remove MS Word's inline styles when copying and pasting.
            paste_remove_spans: true,
            paste_auto_cleanup_on_paste : true,
            paste_remove_styles: true,
            paste_remove_styles_if_webkit: true,
            paste_strip_class_attributes: true,

            // don't strip anything since this is handled by bleach
            valid_elements: "+*[*]",
            valid_children: "+button[a]",

            content_css: window.__tinymce_css

    	});

    }

});
