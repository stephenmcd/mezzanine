
function CustomFileBrowser(field_name, url, type, win) {
    
    var cmsURL = "/admin/filebrowser/browse/?pop=2";
    cmsURL = cmsURL + "&type=" + type;
    
    tinyMCE.activeEditor.windowManager.open({
        file: cmsURL,
        width: 820,  // Your dimensions may differ - toy around with them!
        height: 500,
        resizable: "yes",
        scrollbars: "yes",
        inline: "no",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: "no"
    }, {
        window: win,
        input: field_name,
        editor_id: tinyMCE.selectedInstance.editorId
    });
    return false;
}

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
    cleanup: false,
    forced_root_block: "p",
    remove_trailing_nbsp: true,
    
    // callbackss
    file_browser_callback: "CustomFileBrowser",
    
    // theme_advanced
    theme_advanced_toolbar_location: "top",
    theme_advanced_toolbar_align: "left",
    theme_advanced_statusbar_location: "",
    theme_advanced_buttons1: "bold,italic,|,link,unlink,|,image,|,media,charmap,|,code,|,table,|,bullist,numlist,blockquote,|,undo,redo,|,formatselect",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",
    theme_advanced_path: false,
    theme_advanced_blockformats: "p,h2,h3,h4,pre",
    theme_advanced_styles: "[all] clearfix=clearfix;[p] small=small;[img] Image left-aligned=img_left;[img] Image left-aligned (nospace)=img_left_nospacetop;[img] Image right-aligned=img_right;[img] Image right-aligned (nospace)=img_right_nospacetop;[img] Image Block=img_block;[img] Image Block (nospace)=img_block_nospacetop;[div] column span-2=column span-2;[div] column span-4=column span-4;[div] column span-8=column span-8",
    theme_advanced_resizing : true,
    theme_advanced_resize_horizontal : false,
    theme_advanced_resizing_use_cookie : true,
    theme_advanced_styles: "Image left-aligned=img_left;Image left-aligned (nospace)=img_left_nospacetop;Image right-aligned=img_right;Image right-aligned (nospace)=img_right_nospacetop;Image Block=img_block",
    advlink_styles: "intern=internal;extern=external",
    
    // plugins
    plugins: "advimage,advlink,paste,media,table",
    advimage_update_dimensions_onchange: true,

    // remove MS Word's inline styles when copying and pasting.
    paste_remove_spans: true,
    paste_auto_cleanup_on_paste : true,
    paste_remove_styles: true,
    paste_remove_styles_if_webkit: true,
    paste_strip_class_attributes: true,
    
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
    + "img[class|src|alt=|width|height]," + 
    + "-h2,-h3,-h4," + 
    + "-pre," +
    + "-blockquote," +
    + "-code," + 
    + "-div",
    extended_valid_elements: "pre[style],"
    + "a[name|class|href|target|title|onclick],"
    + "img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],"
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
    +"param[id|name|type|value|valuetype<DATA?OBJECT?REF],",
    valid_child_elements : ""
    + "h1/h2/h3/h4/h5/h6/a[%itrans_na],"
    + "table[thead|tbody|tfoot|tr|td],"
    + "strong/b/p/div/em/i/td[%itrans|#text],"
    + "body[%btrans|#text]"
});
