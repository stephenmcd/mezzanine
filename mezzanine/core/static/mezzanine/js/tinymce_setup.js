
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

if (typeof tinyMCE != 'undefined') {

    tinyMCE.init({

        // main settings
        mode : "specific_textareas",
        editor_selector : "mceEditor",
        theme: "advanced",
        language: "en",
        dialog_type: "window",
        editor_deselector : "mceNoEditor",

        // general settings
        width: '700',
        height: '350',
        indentation : '10px',
        fix_list_elements : true,
        relative_urls: false,
        remove_script_host : true,
        accessibility_warnings : false,
        object_resizing: false,
        //cleanup: false, // SETTING THIS TO FALSE WILL BREAK EMBEDDING YOUTUBE VIDEOS
        forced_root_block: "p",
        remove_trailing_nbsp: true,

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

        // allow inline styles
        inline_styles : true,

        // elements
        valid_elements : ""
		+ "span[style],"
		+ "-p,"
		+ "a[href|target=_blank|class],"
		+ "-strong/-b,"
		+ "-em/-i,"
		+ "-u,"
		+ "-ol,"
		+ "-ul,"
		+ "-li,"
		+ "-dl,"
		+ "-dd,"
		+ "-dt,"
		+ "br,"
		+ "img[class|src|alt=|width|height],"
		+ "-h1,-h2,-h3,-h4,"
		+ "-pre,"
		+ "-blockquote,"
		+ "-cite,"
		+ "-code,"
		+ "-iframe,"
		+ "-table[border=0|cellspacing|cellpadding|width|frame|rules|height|"
		+ "align|summary|bgcolor|background|bordercolor],"
		+ "-tr[rowspan|width|height|align|valign|bgcolor|"
		+ "background|bordercolor],"
		+ "tbody,"
		+ "thead,"
		+ "tfoot,"
		+ "#td[colspan|rowspan|width|height|align|valign|bgcolor|background|"
		+ "bordercolor|scope],"
		+ "#th[colspan|rowspan|width|height|align|valign|scope],"
		+ "-div,"
		+ "",
        extended_valid_elements: "pre[style],"
        + "a[name|class|href|target|title|onclick|rel],"
        + "img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name|style],"
        + "iframe[src|title|byline|portrait|frameborder|width|height],"
        + "br[clearfix],"
        + "-p[class<clearfix?summary?code],"
        + "h2[class<clearfix],h3[class<clearfix],h4[class<clearfix],"
        + "ul[class<clearfix],ol[class<clearfix],"
        + "div[class],"
        + "object[align<bottom?left?middle?right?top|archive|border|class|classid"
          + "|codebase|codetype|data|declare|dir<ltr?rtl|height|hspace|id|lang|name"
          + "|onclick|ondblclick|onkeydown|onkeypress|onkeyup|onmousedown|onmousemove"
          + "|onmouseout|onmouseover|onmouseup|standby|style|tabindex|title|type|usemap"
          + "|vspace|width],"
          + "embed[name|src|type|allowscriptaccess|allowfullscreen|width|height],"
        +"param[id|name|type|value|valuetype<DATA?OBJECT?REF],",
        valid_children : ""
        + "h1/h2/h3/h4/h5/h6/a[%itrans_na],"
        + "table[thead|tbody|tfoot|tr|td],"
        + "strong/b/p/div/em/i/td[%itrans|#text],"
		//+ "body[%btrans|#text]"
        + "",
	});

}
