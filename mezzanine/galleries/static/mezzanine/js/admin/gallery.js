var ZipImporter = function(selector) {
    this.element = $(selector);

    if(!this.supported())
	return;

    this.browseButton = $('button', selector);
    this.fileInput = $('input[type="file"]', selector);
    this.progress = $('.progress');
    this.progressBar = $('.progress .bar', selector);
    this.fileQueue = $('.file-queue', selector);

    this.deferredQueue = $.Deferred();
    this.deferredQueue.resolve();

    this.browseButton.bind('click', $.proxy(this._handleClick, this));
    this.fileInput.bind('change', $.proxy(this._handleFileChange, this));
}

ZipImporter.prototype._handleClick = function(e)
{
    this.fileInput.click();

    return false;
}

ZipImporter.prototype._handleFileChange = function(e)
{
    if(e.currentTarget.files.length > 0)
    {
	this.progressBar.text("");
	this.progressBar.removeClass("error");
	this.progressBar.removeClass("processing");
	
	this.progress.fadeIn('fast');

	var dNext = this.deferredQueue;
	$.each(e.currentTarget.files, $.proxy(function(i, file) {
	    console.log(file);
	    this.fileQueue.append("<li>" + file.name + "</li>");

	    dNext = dNext.pipe($.proxy(function() {
		return this.uploadFile(file);
	    }, this));
	}, this));

	/* Prevent these files from being submitted again */
	this.fileInput.val("");
    }
}

ZipImporter.prototype.supported = function() {
    var xhr = new XMLHttpRequest();
    var result = !! (xhr && ('upload' in xhr) && ('onprogress' in xhr.upload));

    if(result)
    {
	$(".form-row.zip_import").remove();
	$(this.element).show();
    }
    return true;
}

ZipImporter.prototype.uploadFile = function(file)
{
    var d = $.Deferred();

    this.progressBar.text(file.name);
    var queueItem = this.fileQueue.children()[0];
    $(queueItem).detach();

    var xhr = new XMLHttpRequest();
    xhr.upload.onprogress = $.proxy(function(e) {
	var done = e.position || e.loaded, total = e.totalSize || e.total;
	this.progressBar.width((Math.floor(done/total*1000)/10) + "%");
	if(done == total)
	{
	    this.progressBar.text("Processing " + file.name);
	    this.progressBar.addClass("processing");
	}
    }, this);

    xhr.onreadystatechange = $.proxy(function(e) {
	if(xhr.readyState == 4)
	{
	    this.progressBar.removeClass("processing");
	    if(xhr.status == 200)
	    {
		this.progressBar.text("Done");
		d.resolve();
	    }
	    else
	    {
		this.progressBar.text("Error on " + file.name);
		this.progressBar.addClass("error");
		d.reject();
	    }
	}
    }, this);


    var fd = new FormData($('form')[0]);
    fd.append('zip_import', file);

    xhr.open('post', '', true);
    xhr.send(fd);

    return d.promise();
}

$(function() {
    var zipImporter = new ZipImporter("#zipimporter-fieldset");
});

