$(function() {
    $('div.form-row.zip_import').remove();

    $('#zip-import-button').click(function (e) {
	$('#zip-import-file').click();
	return false;
    });

    $("#zip-import-file").bind('change', function(e) {
	if(e.currentTarget.files.length > 0)
	{
	    $('#zip-import-button').attr("disabled", "disabled");

	    $('#zip-import-progress .bar').text("");
	    $('#zip-import-progress .bar').removeClass("error");
	    $('#zip-import-progress .bar').removeClass("processing");
	    $('#zip-import-progress').fadeIn('fast');

	    var file = e.currentTarget.files[0];

	    var xhr = new XMLHttpRequest();
	    xhr.upload.onprogress = function(e) {
		var done = e.position || e.loaded, total = e.totalSize || e.total;
		$("#zip-import-progress .bar").width((Math.floor(done/total*1000)/10) + "%");
		if(done == total)
		{
		    $('#zip-import-progress .bar').text("Processing");
		    $('#zip-import-progress .bar').addClass("processing");
		}
	    };

	    xhr.onreadystatechange = function(e) {
		if(xhr.readyState == 4)
		{
		    if(xhr.status == 200)
		    {
			document.location.reload();
		    }
		    else
		    {
			$('#zip-import-progress .bar').text("Error");
			$('#zip-import-progress .bar').removeClass("processing");
			$('#zip-import-progress .bar').addClass("error");
			$('#zip-import-button').removeAttr("disabled");
		    }
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
