var show_disabled = false;
var sw_server = 'http://nextmove/smallworld';
var sw_server = './';

function toggle_visibility() {
	$button = $('#vis-button');
	if (show_disabled) {
		$button.addClass('fa-eye');
		$button.removeClass('fa-eye-slash');
		$button.attr('title', 'Hide disabled datasets');
	} else {
		$button.addClass('fa-eye-slash');
		$button.removeClass('fa-eye');
		$button.attr('title', 'Show disabled datasets');
	}
	show_disabled = !show_disabled;
	refresh(false);
}

function send_data(data) {
	return function() {
		$.ajax({
			url: sw_server + '/maps/modify/' + data.key,
			dataType: 'json',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			type: 'POST',
			data: JSON.stringify({
				name: data.name,
				url: data.url,
				prefix: data.prefix,
				enabled: data.enabled
			}),
			success: function(res) {
				refresh(false);
			}
		});
	}.bind(data);
}

function queue_change_on_box(box) {
	clearTimeout(box.data('send'));
	box.data('send', setTimeout(send_data(box.data('cfg')), 800));
}

function make_add_box() {
	var $box = $('<div id="add-new" class="sw-mapfile-box static">');
	var $top = $('<table class="sw-mapfile-top">');
	var $bot = $('<table class="sw-mapfile-bottom">');
	var $addButton = $('<i class="fa fa-upload" aria-hidden="true"></i>');
	var $nameInput = $('<input name="name" type="text" placeholder="New Dataset...">');
	$addButton.css('cursor', 'pointer');
	$addButton.click(function(box) {
		var $nameinput = $('input[name=name]', $box);
		var $fileinput = $('input[type=file]', $box);
		var name = $nameinput.val();
		var tFlash = 250;
		var okay = true;
		// check fileinput
		if (!$fileinput.val()) {
			$fileinput.stop().fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash);
			okay = false;
		}
		if (name.length == 0) {
			$nameinput.focus();
			$nameinput.stop().fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash);
			okay = false;
		}
		if (okay) {
			var formData = new FormData($('form', box)[0]);
			var $add = $('#add-new');
			var fade = setInterval((function($elem) {
				$elem.fadeTo(800, 0.5).fadeTo(800, 1);
			}).bind(null, $add), 1600);
			$.ajax({
				url: sw_server + '/maps/upload',
				type: 'POST',
				data: formData,
				async: true,
				cache: false,
				contentType: false,
				processData: false,
				success: function(returndata) {
					refresh(false);
					clearInterval(fade);
				}
			});
		}
	}.bind(null, $box));
	// tooltips
	$addButton.attr('title', 'Add a new dataset');
	$top.append($('<tr>').append($('<td>').append('<i class="fa fa-database" aria-hidden="true"></i>')).append($('<td>').append($nameInput)).append($('<td>').append($addButton)));
	var $fileInput = $('<input name="file" type="file">');
	var $urlInput = $('<input name="url" type="text">').attr('placeholder', '...');
	var $prefixInput = $('<input name="prefix" type="text">').attr('placeholder', '...');
	$bot.append($('<tr>').append($('<td>').attr('colspan', 2).append($fileInput)));
	$bot.append($('<tr>').append($('<td>').append('Id URL')).append($('<td>').append($urlInput)));
	$bot.append($('<tr>').append($('<td>').append('Id Prefix')).append($('<td>').append($prefixInput)));
	$box.append($('<div>').append($('<form>').append($top, $bot)));
	return $box;
}

function update_mapfile_priority() {
	var $boxes = $('#sw-mapfiles').children();
	var priority = $.map($.grep($.map($boxes, function(e) {
		return $(e).data('cfg');
	}), function(e) {
		return e;
	}), function(e) {
		return e.key
	});
	$.ajax({
		url: sw_server + '/maps/setpriority/',
		dataType: 'json',
		type: 'POST',
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
		data: JSON.stringify(priority)
	});
}

function make_swmapfile_box(data) {
	var $box = $('<div class="sw-mapfile-box">');
	var $top = $('<table class="sw-mapfile-top">');
	var $bot = $('<table class="sw-mapfile-bottom">');
	$box.data('cfg', data);
	var $enabledIndicator = $('<i class="fa fa-database" aria-hidden="true"></i>');
	var $nameInput = $('<input type="text">');
	var $mmapIndicator = $('<i class="fa fa-microchip" aria-hidden="true"></i>');
	var $bloomIndicator = $('<i class="fa fa-filter" aria-hidden="true"></i>');
	var $extIndicator = $('<i class="fa fa-coins" aria-hidden="true"></i>');
	$enabledIndicator.css('cursor', 'pointer');
	// tooltips
	$enabledIndicator.attr('title', 'Enabled/Disable Dataset');
	$mmapIndicator.attr('title', 'Resident Memory');
	$bloomIndicator.attr('title', 'Bloom Filter');
	$extIndicator.attr('title', 'Index Extensions');
	if (!data.enabled) $box.addClass('disabled');
	if (data.memoryMapped) $mmapIndicator.addClass('disabled');
	if (!data.bloomFiltered) $bloomIndicator.addClass('disabled');
	if (!data.extended) $extIndicator.addClass('disabled');
	$enabledIndicator.click(function(box) {
		box.toggleClass('disabled');
		box.data('cfg').enabled = !box.data('cfg').enabled;
		queue_change_on_box(box);
	}.bind(null, $box));
	$nameInput.keyup(function(box) {
		box.data('cfg').name = this.val();
		queue_change_on_box(box);
	}.bind($nameInput, $box));
	$nameInput.attr('value', data.name);
	$top.append($('<tr>').append($('<td>').append($enabledIndicator)).append($('<td>').append($nameInput)).append($('<td>').append($mmapIndicator)).append($('<td>').append($bloomIndicator)).append($('<td>').append($extIndicator)));
	var $urlInput = $('<input type="text">').attr('value', data.url).attr('placeholder', '...');
	var $prefixInput = $('<input type="text">').attr('value', data.prefix).attr('placeholder', '...');
	$urlInput.keyup(function(box) {
		box.data('cfg').url = this.val();
		queue_change_on_box(box);
	}.bind($urlInput, $box));
	$prefixInput.keyup(function(box) {
		box.data('cfg').prefix = this.val();
		queue_change_on_box(box);
	}.bind($prefixInput, $box));
	if (data.status == 'Mapping' || data.status == 'Premapping') {
		setInterval((function($elem) {
			$elem.fadeTo(800, 0.5).fadeTo(800, 1);
		}).bind(null, $box), 1600);
	}
	if (data.status == 'Mapping' || data.numMapped > 0) {
		var tot = data.numMapped + data.numUnmapped;
		var str = tot + '/' + data.numEntries + '[' + data.numMapped + '|' + data.numSkipped + ']';
		$bot.append($('<tr>').append($('<td class="progress">').attr('colspan', 2).append(new_progressbar(data.key, data.numMapped, data.numUnmapped, data.numSkipped, data.numEntries, 10))));
	} else if (data.status == 'Premapping') {
		$bot.append($('<tr>').append($('<td class="progress">').attr('colspan', 2).append(new_premapbar(data.key, data.premapProgress, 10))));
	} else if (data.status == 'Queued') {
		$bot.append($('<tr>').append($('<td class="progress">').attr('colspan', 2).append(data.status)));
	}
	$bot.append($('<tr>').append($('<td>').append('Location')).append($('<td>').append(data.filePath)));
	$bot.append($('<tr>').append($('<td>').append('Id URL')).append($('<td>').append($urlInput)));
	$bot.append($('<tr>').append($('<td>').append('Id Prefix')).append($('<td>').append($prefixInput)));
	$box.append($('<div>').append($top, $bot));
	return $box;
}

function refresh(auto) {
	$.get(sw_server + "/search/maps", function(d) {
		var $mapfiles = $('#sw-mapfiles');
		var makesortable = false;
		// first update
		if ($mapfiles.children().length == 0) {
			var $add = make_add_box();
			$mapfiles.empty();
			var keys = Object.keys(d);
			$.each(keys, function(i, e) {
				var val = d[e];
				val.key = e;
				if (val.status != 'Missing' && (show_disabled || val.enabled)) $mapfiles.append(make_swmapfile_box(val));
			})
			$mapfiles.append($add);
			$("#sw-mapfiles").sortable({
				update: update_mapfile_priority,
				items: '.sw-mapfile-box:not(.static)',
				revert: true
			});
			$("#sw-mapfiles div").disableSelection();
		}
		// fresh update
		else {
			var $boxes = $mapfiles.children();
			$.each($boxes, function(i, e) {
				$elem = $(e);
				var curr = $elem.data('cfg');
				if (curr) {
					if (!d[curr.key]) {
						$elem.remove();
					} else {
						if (d[curr.key].status != curr.status) {
							d[curr.key].key = curr.key;
							$elem.replaceWith(make_swmapfile_box(d[curr.key]));
						} else if (curr.status == 'Mapping') {
							// update counters
							curr.numMapped = d[curr.key].numMapped;
							curr.numUnmapped = d[curr.key].numUnmapped;
							curr.numSkipped = d[curr.key].numSkipped;
							curr.numEntries = d[curr.key].numEntries;
							var tot = curr.numMapped + curr.numUnmapped;
							var str = tot + '/' + curr.numEntries + '[' + curr.numMapped + '|' + curr.numSkipped + ']';
							$('.progress', $elem).html(new_progressbar(curr.key, curr.numMapped, curr.numUnmapped, curr.numSkipped, curr.numEntries, 10));
						} else if (curr.status == 'Premapping') {
							curr.premapProgress = d[curr.key].premapProgress;
							$('.progress', $elem).html($('<tr>').append($('<td class="progress">').attr('colspan', 2).append(new_premapbar(curr.key, curr.premapProgress, 10))));
						} else if (!curr.enabled && !show_disabled) {
							$elem.remove();
						}
						delete d[curr.key];
					}
				}
			});
			var $add = $('#add-new');
			var keys = Object.keys(d);
			$.each(keys, function(i, e) {
				var val = d[e];
				val.key = e;
				if (val.status != 'Missing' && (show_disabled || val.enabled)) $add.before(make_swmapfile_box(val));
			})
		}
		// recall if
		var $boxes = $mapfiles.children();
		var setupdate = false;
		$.each($boxes, function(i, e) {
			$elem = $(e);
			var curr = $elem.data('cfg');
			if (curr && (curr.status == 'Premapping' || curr.status == 'Mapping' || curr.status == 'Loading')) {
				setupdate = true;
			}
		});
		if (auto) {
			if (setupdate) setTimeout(function() {
				return refresh(true)
			}, 500);
			else setTimeout(function() {
				return refresh(true)
			}, 6000);
		}
	});
}
$(function() {
	refresh(true);
});