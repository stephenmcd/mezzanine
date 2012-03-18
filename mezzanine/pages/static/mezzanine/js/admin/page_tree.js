
var cookie = 'mezzanine-admin-tree';
var at = ('; ' + document.cookie).indexOf('; ' + cookie + '=');
var ids = '';

if (at > -1) {
    ids = document.cookie.substr(at + cookie.length + 1).split(';')[0];
}

var toggleID = function(opened, id) {
    // Add or remove the page ID from the cookie IDs string.
    var index = $.inArray(id, ids.split(','));
    if (opened) {
        if (index == -1) {
            if (ids) {ids += ',';}
            ids += id;
        }
    } else if (index > -1) {
        ids = ids.split(',');
        ids.splice(index, 1);
        ids = ids.join(',');
    }
    document.cookie = cookie + '=' + ids + '; path=/';
};

function showButtonWithChildren() {
	$('li:has(li) .tree-toggle').css({visibility: 'visible'});
	$('li:not(:has(li)) .tree-toggle').css({visibility: 'hidden'});
}

$(function() {

	showButtonWithChildren();

    if (window.__grappelli_installed) {
        $('.delete').addClass('grappelli-delete');
    }

    // There's a weird bug where the first click on a page name
    // does nothing. If we remove the call to showButtonWithChildren
    // it works fine, which doesn't make sense. So this click handler
    // forces the anchors to go to their location.
    $('#tree .changelink').click(function() {
        location.href = $(this).attr('href');
        return false;
    });

    $('#tree .tree-toggle').click(function() {
        // Show/hide the branch and toggle the icon.
        var pageLink = $(this);
        pageLink.parent().parent().find('ul:first').toggle();
        pageLink.find('.icon').toggle();
        // Add or remove the page ID from the cookie.
        var opened = pageLink.find('.close:visible').length == 1;
        var id = pageLink.attr('id').split('-')[1];
        toggleID(opened, id);
        return false;
    });

    // Show previously opened branches.
    if (ids) {
    	$('#page-' + ids.split(',').join(', #page-')).each(function(){
			var pageLink = $(this);
			pageLink.parent().parent().find('ul:first').toggle();
			pageLink.find('.close').css('display', 'inline');
			pageLink.find('.open').css('display', 'none');
		});
	}

    // The dropdown list for adding a new page contains URLs for each
    // model - redirect when selected.
    $('.addlist').change(function() {
        // Ensure the branch is saved as open when adding to it so that
        // the new branch will be visible directly after saving.
        var id = $(this).attr('id');
        if (id) {
            toggleID(true, id.split('-')[1]);
        }
        var addUrl = this[this.selectedIndex].value;
        if (addUrl) {
            location.href = addUrl;
        }
        this.selectedIndex = 0;
        return true;
    });

    // AJAX callback that's triggered when dragging a page to re-order
    // it has ended.
    var updateOrdering = function(event, ui) {
        var args = {
            'ordering_from': $(this).sortable('toArray').toString(),
            'ordering_to': $(ui.item).parent().sortable('toArray').toString(),
        };
        if (args['ordering_from'] != args['ordering_to']) {
            // Branch changed - set the new parent ID.
            args['moved_page'] = $(ui.item).attr('id');
            args['moved_parent'] = $(ui.item).parent().parent().attr('id');
            if (args['moved_parent'] == 'tree') {
                delete args['moved_parent'];
            }
        } else {
            delete args['ordering_to'];
        }
        $.post(window.__page_ordering_url, args, function(data) {
            if (data !== "ok") {
                alert("Error occured: " + data + "\nOrdering wasn't updated.");
            }
        });
		showButtonWithChildren();
    };

    // Make the pages sortable via drag and drop.
    // The `connectWith` option needs to be set separately to get
    // around a performance bug with `sortable`.
    $('#tree ul').sortable({
        handle: '.ordering', opacity: '.7', stop: updateOrdering,
        forcePlaceholderSize: true, placeholder: 'placeholder',
        revert: 150, toleranceElement: ' div'
    }).sortable('option', 'connectWith', '#tree ul');
    $('#tree ul').disableSelection();

});
