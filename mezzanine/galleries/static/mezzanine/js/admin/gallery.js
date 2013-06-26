$(function() {
    $('#zip-import-button').click(function (e) {
	$('#zip-import-file').click();
	return false;
    });

    $("#zip-import-file").bind('change', function(e) {
	if(e.currentTarget.files.length > 0)
	{
	    $('#zip-import-progress .bar').text("");
	    $('#zip-import-progress').fadeIn('fast');

	    var file = e.currentTarget.files[0];

	    var xhr = new XMLHttpRequest();
	    xhr.upload.onprogress = function(e) {
		var done = e.position || e.loaded, total = e.totalSize || e.total;
		$("#zip-import-progress .bar").width((Math.floor(done/total*1000)/10) + "%");
	    };

	    xhr.onreadystatechange = function(e) {
		if(xhr.readyState == 4)
		{
		    $('#zip-import-progress .bar').text("Complete");
		    $('#zip-import-file').val("");
		}
	    };

	    var fd = new FormData($('form')[0]);
	    fd.append('zip_import', file);

	    xhr.open('post', '', true);
	    xhr.send(fd);
	}
    });
});
