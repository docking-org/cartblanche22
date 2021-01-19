var sw_server;
sw_server = '10.20.0.1:5010'; // nm debug deployment
// sw_server = 'http://gpcr:xtal@swp.docking.org'; // nm debug deployment
var config = {};
var source = false;
var distance_cols = $.map("tdn,tup,rdn,rup,ldn,lup,mut,maj,min,hyb,sub".split(","), function (e) {
    return {
        title: e.toUpperCase(),
        name: e,
        class: 'editop',
        width: '38px',
        sortable: true,
        searchable: true
    };
});
var datasets = {};
var dtable = null;
var search_state = null;
var fromSmiInput = false;
/* Configuration and options */

$(document).ready(function () {
    console.log("config working");
    console.log(sw_server + '/search/config');
    // $.ajax({
    //     url: sw_server + '/search/config',
    //     type: 'GET',
    //       dataType: 'json',
    //       contentType:'application/json',
    //       beforeSend: function (xhr) {
    //         xhr.setRequestHeader ("Authorization", "Basic gpcr:xtal");
    //       },
    //     success: function (res) {
    //         console.log('res', res)
    //         config = res;
    //         if (!config.WebApp.SearchAsYouDraw)
    //             $('.swopt').removeClass('searchasyoudraw');
    //         add_scoretype_selection(config);
    //         toggle_scoring();
    //     },
    //     error: function (responseData, textStatus, errorThrown) {
    //         alert('GET failed.');
    //     }
    // });


    $.get(sw_server + '/search/config', function (res) {
    	console.log('res', res)
    	config = res;
    	if (!config.WebApp.SearchAsYouDraw)
    		$('.swopt').removeClass('searchasyoudraw');
    	add_scoretype_selection(config);
    	toggle_scoring();
    });
});

function norm_score_name(x) {
    return x.replace(new RegExp(' ', 'g'), '_').toLowerCase();
}

function add_scoretype_selection(config) {
    console.log(config)
    $.each(config.ScoreFuncs, function (i, e) {
        if (e.name == "ECFP4" || e.name == "Daylight") {
            e.enabledByDefault = true
        }
        $('#swscore').append($('<tr>').append($('<th>').append(e.name)).append($('<td>').addClass('spacer')).append($('<td>').append($('<input>').attr('type', 'checkbox').addClass('scorefunc').attr('name', norm_score_name(e.name)).attr('checked', e.enabledByDefault).change(toggle_scoring))).append($('<td>').css('font-style', 'italic').append(e.description ? e.description : '')));
    });
}

function get_active_scores() {
    return config.ScoreFuncs ? $.grep(config.ScoreFuncs, function (e) {
        return $('input[name=' + norm_score_name(e.name) + ']').is(':checked');
    }) : [];
}

function has_atom_alignment() {
    return $.grep(get_active_scores(), function (e) {
        return e.type === 'com.nmsoftware.smallworld.score.AtomScore';
    }).length != 0;
}

function get_score_columns() {
    var active = $.grep(get_active_scores(), function (e) {
        return e.type !== 'com.nmsoftware.smallworld.score.AtomScore';
    });
    var cols = $.map(active, function (e) {
        return {
            title: e.name,
            name: e.name.toLowerCase(),
            sortable: true,
            searchable: true,
            width: "40px",
            render: flex_renderer
        };
    });
    return cols;
}

/* Util */
function toggle_scoring() {
    if (dtable) {
        $('#results').dataTable().fnDestroy();
        $('#results').empty();
        dtable = null;
    }
    update_visible_columns();
    toggle_color();
    refresh();
}

function toggle_color() {
    var optColEdits = $('input[name=optColEdits]');
    $('#key').css('display', optColEdits.prop('checked') ? 'table' : 'none');
    redraw();
}

function toggle_align() {
    var $optAlign = $('input[name=optAlign]');
    redraw();
}

/* Db Info */
function db_maps(select) {
    $.get(sw_server + '/search/maps', function (data) {
        for (var key in data) {
            datasets[key] = data[key];
            if (data[key].enabled === true && data[key].status === 'Available') {
                select.append('<option value=' + key + '>' + data[key].name + '</option>');
            }
        }
    });
}

/* Range Sliders */
function install_range_slider(param, limit) {
    if (!limit) {
        limit = 10;
    }
    var lb = $("input[name='" + param + "lb']");
    var ub = $("input[name='" + param + "ub']");
    var range = $('#' + param + 'slider').slider({
        min: 0,
        max: limit,
        range: true,
        values: [lb.val(), ub.val()],
        slide: function (event, ui) {
            lb.val(ui.values[0]);
            ub.val(ui.values[1]);
            update_bound(param, false);
        }
    });
    lb.prop('readonly', true);
    ub.prop('readonly', true);
    lb.css('background-color', 'transparent');
    ub.css('background-color', 'transparent');
    lb.css('background-color', 'transparent');
    lb.css('border', 'none');
    ub.css('border', 'none');
    lb.change(function () {
        range.slider('values', 0, lb.val());
        range.slider('values', 1, ub.val());
    });
    ub.change(function () {
        range.slider('values', 0, lb.val());
        range.slider('values', 1, ub.val());
    });
}

function set_range(param, lo, hi, enabled) {
    var range = $('#' + param + 'slider');
    var lb = $("input[name='" + param + "lb']");
    var ub = $("input[name='" + param + "ub']");
    lb.val(lo);
    ub.val(hi);
    lb.prop('disabled', !enabled);
    ub.prop('disabled', !enabled);
    range.slider('option', 'disabled', !enabled);
    range.slider('values', 0, lo);
    range.slider('values', 1, hi);
}

function update_bounds() {
    update_bound('dist', true);
    update_bound('topodist', true);
    update_bound('tdn', true);
    update_bound('tup', true);
    update_bound('rdn', true);
    update_bound('rup', true);
    update_bound('ldn', true);
    update_bound('lup', true);
    update_bound('maj', true);
    update_bound('min', true);
    update_bound('sub', true);
    update_bound('hyb', true);
    dtable.draw();
}

function update_visible_columns() {
    if (!dtable) {
        return;
    }
    var optAdvanced = $('input[name=optAdv]').prop('checked');
    var optAtMatch = has_atom_alignment();
    dtable.column("mut:name").visible(optAdvanced && optAtMatch);
    dtable.column("maj:name").visible(optAdvanced && optAtMatch);
    dtable.column("min:name").visible(optAdvanced && optAtMatch);
    dtable.column("sub:name").visible(optAdvanced && optAtMatch);
    dtable.column("hyb:name").visible(optAdvanced && optAtMatch);
    dtable.column("tdn:name").visible(optAdvanced);
    dtable.column("tup:name").visible(optAdvanced);
    dtable.column("rdn:name").visible(optAdvanced);
    dtable.column("rup:name").visible(optAdvanced);
    dtable.column("ldn:name").visible(optAdvanced);
    dtable.column("lup:name").visible(optAdvanced);
    dtable.column("topodist:name").visible(optAdvanced);
}

// Update the bound on a search parameter
function update_bound(param, nodraw) {
    update_bound_range(param, $("input[name='" + param + "lb']").val(), $("input[name='" + param + "ub']").val(), nodraw);
}

// Update the bound on a search parameter specifying the new range
// apply the bounds as a filter on the table column, If the upper bound
// exceeds that of the current search state a new search is started
function update_bound_range(param, lb, ub, nodraw) {
    if (dtable == null || search_state == null) {
        return; // search not started
    }
    if (ub > search_state[param]) {
        refresh();
    }
    if (lb === 0 && ub === search_state[param]) {
        dtable.column(param + ":name").search('');
    } else {
        dtable.column(param + ":name").search(lb + "-" + ub);
    }
    if (!nodraw) {
        dtable.draw();
    }
}

function set_mode() {
    var val = $("select[name='mode'] option:selected").val();
    if (val === 'swsub') {
        set_mode_sw_subsearch();
    } else if (val === 'swsup') {
        set_mode_sw_supsearch();
    } else if (val === 'swmcs') {
        set_mode_sw_mcssearch();
    } else if (val === 'swsim') {
        set_mode_sw_simsearch();
    } else if (val === 'swmurko') {
        set_mode_sw_murko();
    } else if (val === 'swskel') {
        set_mode_sw_skel();
    }
    update_bounds();
}

function set_mode_sw_supsearch() {
    set_range('tup', 0, 0, false);
    set_range('tdn', 0, 10, true);
    set_range('rup', 0, 0, false);
    set_range('rdn', 0, 10, true);
    set_range('lup', 0, 0, false);
    set_range('ldn', 0, 0, false);
    set_range('maj', 0, 0, false);
    set_range('min', 0, 0, false);
}

function set_mode_sw_subsearch() {
    set_range('tup', 0, 10, true);
    set_range('tdn', 0, 0, false);
    set_range('rup', 0, 10, true);
    set_range('rdn', 0, 0, false);
    set_range('lup', 0, 0, false);
    set_range('ldn', 0, 0, false);
    set_range('maj', 0, 0, false);
    set_range('min', 0, 0, false);
}

function set_mode_sw_mcssearch() {
    set_range('tup', 0, 10, true);
    set_range('tdn', 0, 10, true);
    set_range('rup', 0, 10, true);
    set_range('rdn', 0, 10, true);
    set_range('lup', 0, 0, false);
    set_range('ldn', 0, 0, false);
    set_range('maj', 0, 0, false);
    set_range('min', 0, 0, false);
}

function set_mode_sw_simsearch() {
    set_range('tup', 0, 10, true);
    set_range('tdn', 0, 10, true);
    set_range('rup', 0, 10, true);
    set_range('rdn', 0, 10, true);
    set_range('lup', 0, 10, true);
    set_range('ldn', 0, 10, true);
    set_range('maj', 0, 10, true);
    set_range('min', 0, 10, true);
}

function set_mode_sw_murko() {
    set_range('tup', 0, 10, true);
    set_range('tdn', 0, 10, true);
    set_range('rup', 0, 0, false);
    set_range('rdn', 0, 0, false);
    set_range('lup', 0, 0, false);
    set_range('ldn', 0, 0, false);
    set_range('maj', 0, 10, true);
    set_range('min', 0, 10, true);
}

function set_mode_sw_skel() {
    set_range('tup', 0, 0, false);
    set_range('tdn', 0, 0, false);
    set_range('rup', 0, 0, false);
    set_range('rdn', 0, 0, false);
    set_range('lup', 0, 0, false);
    set_range('ldn', 0, 0, false);
    set_range('maj', 0, 0, false);
    set_range('min', 0, 0, false);
}

/* Search Control */
function refresh() {
    set_smiles(newSearch)
}

function molChanged(smiles) {
    if (config.WebApp.SearchAsYouDraw)
        newSearch(smiles);
    //adding hg database check
    checkHg(smiles, $('#exampleModalLong'), $('#hgData'), search_state.db)
}

function newSearch(smiles) {
    if (!smiles)
        return;
    if (!!window.EventSource) {
        stopStreaming();
        // Store the search parameters
        search_state = {
            smi: smiles,
            db: $("select[name='db'] option:selected").val(),
            dist: $("input[name='distub']").val(),
            topodist: $("input[name='topodistub']").val(),
            tdn: $("input[name='tdnub']").val(),
            tup: $("input[name='tupub']").val(),
            rdn: $("input[name='rdnub']").val(),
            rup: $("input[name='rupub']").val(),
            ldn: $("input[name='ldnub']").val(),
            lup: $("input[name='lupub']").val(),
            maj: $("input[name='majub']").val(),
            min: $("input[name='minub']").val(),
            sub: $("input[name='subub']").val(),
            scores: $.map(get_active_scores(), function (e) {
                return e.name
            }).join(",")
        };
        source = new EventSource(sw_server + '/search/submit?smi=' + encodeURIComponent(search_state.smi) + '&db=' + encodeURIComponent(search_state.db) + '&dist=' + search_state.topodist + '&tdn=' + search_state.tdn + '&tup=' + search_state.tup + '&rdn=' + search_state.rdn + '&rup=' + search_state.rup + '&ldn=' + search_state.ldn + '&lup=' + search_state.lup + '&maj=' + search_state.maj + '&min=' + search_state.min + '&sub=' + search_state.sub + '&scores=' + search_state.scores);
        $('#statusspan').html("Waiting...");
    } else {
        console.log("ERROR: Browser does not support server-sent events");
        $('#results').append('<tr><td>Browser does not support Server-Side Events!</td></tr>');
        return;
    }
    source.addEventListener('message', function (e) {
        // console.log(e)
        var d = JSON.parse(e.data);
        if (d.status === "END") {
            redraw();
            stopStreaming();
            $('#statusspan').html("Finished (" + format_search_stats(d) + ")");
        } else {
            if (d.status === "FIRST") {
                // console.log(d);
                $('#statusspan').html("Searching... (" + format_search_stats(d) + ")");
                var url = sw_server + '/search/view/?hlid=' + d.hlid;
                init_table($('#results'), url);
                $('.dataTables_scrollBody').css('background', 'repeating-linear-gradient(45deg, #edeeff, #edeeff 10px, #fff 10px, #fff 20px)');
            } else if (d.status === "MORE") {
                $('#statusspan').html("Searching... (" + format_search_stats(d) + ")");
                redraw();
            } else if (d.status === "MISS") {
                $('#statusspan').html("Query not indexed");
                stopStreaming();
                $('.dataTables_scrollBody').css('background', 'repeating-linear-gradient(45deg, #ffcbaf, #ffcbaf 10px, #fff 10px, #fff 20px)');
            } else {
                $('#statusspan').html("Searching... (" + format_search_stats(d) + ")");
                // ping to check if we're still listening?
            }
        }
    }, false);
    source.addEventListener('error', function (e) {
        stopStreaming();
        redraw();
        $('#statusspan').prepend("Stopped! ");
    }, false);
}

function format_search_stats(stat) {
    var eps = stat.numEdgesPerSec;
    var unit = "TEPS";
    if (eps >= 1000000000) {
        eps /= 1000000000;
        unit = "GTEPS";
    } else if (eps >= 1000000) {
        eps /= 1000000;
        unit = "MTEPS";
    } else if (eps >= 1000) {
        eps /= 1000;
        unit = "KTEPS";
    }
    return stat.elap + " Elapsed, " + Number(eps).toFixed(1) + " " + unit + ", E=" + stat.numEdges + " V=" + stat.numNodes + ", " + stat.numWaveFront + " Wavefront";
}

function resize() {
    if (dtable) {
        var url = dtable.ajax.url();
        $('#results').dataTable().fnDestroy();
        $('#results').empty();
        dtable = null;
        init_table($('#results'), url);
    }
}

function redraw() {
    if (!dtable) {
        return;
    }
    if ($('#results').dataTable().fnSettings() && $('#results').dataTable().fnSettings().oScroller) {
        var s = $('#results').dataTable().fnSettings().oScroller.s;
        s.dt.oApi._fnDraw(s.dt);
    } else {
        dtable.draw('full-hold');
    }
}

function stopStreaming() {
    if (source) source.close();
}

function init_table(table, url) {
    console.log("table initiated")
    if (!dtable) {
        $('#splash').css('display', 'none');
        var columns = [{
            "title": "Compound (<input type='checkbox' name='optColEdits' onchange='toggle_color()'>Color, <input type='checkbox' name='optAlign' onchange='toggle_align()'>Align)",
            "name": "alignment",
            "class": "compound",
            "sortable": false,
            "type": "html",
            "width": "250px",
            "render": hit_renderer,
        }, {
            "title": "Distance",
            "name": "dist",
            "width": "65px",
            "sortable": true
        }].concat(get_score_columns()).concat([{
            "title": "Anon Distance",
            "name": "topodist",
            "width": "65px",
            "sortable": true
        }, {
            "title": "Unlabelled MCES",
            "name": "mces",
            "width": "50px",
            "sortable": true
        }]).concat(distance_cols);
        dtable = table.DataTable({
            "columns": columns,
            destroy: true,
            serverSide: true,
            autoWidth: true,
            filter: true,
            "ajax": {
                "url": url,
                "type": 'GET'
            },
            "dom": 'rtpi',
            "scrollX": true,
            "scrollY": (function () {
                // 10: margin (1*10px), 5: padding (1x5px)
                var height = $('#res-panel').height() - (65 + $('#res-head').height() + 10 + 5 + $('#key').height());
                if (height < 50) {
                    return 800;
                } else {
                    return height;
                }
            })(),
            "deferRender": true,
            "scroller": {
                "rowHeight": 90,
                "loadingIndicator": false,
                "serverWait": 20,
                "displayBuffer": 3
            },
            "order": [
                [0, 'asc']
            ]
        });

    } else {
        dtable.ajax.url(url).load();
    }
    update_bounds();
    update_visible_columns();
}

/* Popup */
function hide_imgpop() {
    $('#imgpop').hide();
}

function show_imgpop(img) {
    var popup = $('#imgpop');
    popup.empty();
    popup.append('<img width="300px" height="180px" src="' + img.src + '"/>');
    var offset = $(img).offset();
    popup.css('left', offset.left + 160 + 'px');
    popup.css('top', offset.top - 50 + 'px');
    popup.show();
}

/*
 * Export the current table view.
 */
function export_results() {
    if (!dtable) {
        return;
    }
    var url = dtable.ajax.url();
    var regex = /hlid=(\d+)/;
    var hlid = regex.exec(url);
    var params = {
        hlid: hlid[1]
    };
    $.each(dtable.order(), function (i, val) {
        params['order[' + i + '][column]'] = val[0];
        params['order[' + i + '][dir]'] = val[1];
    });
    dtable.columns().every(function () {
        var idx = this.index();
        params['columns[' + idx + '][name]'] = $('#results').dataTable().fnSettings().aoColumns[idx].sName;
        if (this.search()) {
            params['columns[' + idx + '][search][value]'] = this.search();
        }
    });
    window.open(sw_server + '/search/export?' + $.param(params));
}

/* Column Rendering */
function drag_img(event, smiles) {
    hide_imgpop();
    var url = config.WebApp.ResolverUrl.replace("%s", encodeURIComponent(smiles));
    console.log(url);
    $.ajax({
        async: false,
        type: 'GET',
        url: url,
        success: function (data) {
            event.dataTransfer.setData("text", data);
        }
    });
}

function flex_renderer(data, type, row) {
    if (typeof data === "number") return data.toFixed(2);
    else return data;
}

function hit_renderer(data, type, row) {
    var table = $("<table class='compound_cell'></table>");
    var img = $('<img width="150px" height="90px" />');
    let button = $('<button class="add">Add to Cart</button>')
    var color = $('input[name="optColEdits"]').prop('checked');
    var align = $('input[name="optAlign"]').prop('checked');
    var base_url = config.WebApp.DepictionUrl;
    var qsmi = align ? data.qryMappedSmiles : '';
    var hsmi = align ? data.hitMappedSmiles : data.hitSmiles;
    var extra = {
        bgcolor: 'clear'
    };
    if (data.atomScore.length && data.atomMap.length) {
        if (false) {
            var cmap = color ? $.map(data.atomScore, function (e, i) {
                return e != 1 ? 1 : 0;
            }).join(',') : "";
            var cols = color ? "0xff0000" : "";
            extra.hgstyle = 'colored';
        } else {
            var cmap = color ? data.atomScore.join(',') : '';
            var cols = color ? "2cbe84,adffab,adffab,fff277,ffb67e,ffbec4" : "";
            extra.hgstyle = 'outerglow';
        }
    } else {
        var cmap = '';
        var cols = '';
    }
    var depict_url = base_url.replace("%s", encodeURIComponent(hsmi))
        .replace("%q", encodeURIComponent(qsmi))
        .replace("%c", encodeURIComponent(cols))
        .replace("%m", encodeURIComponent(cmap))
        .replace("%w", 50).replace("%h", 30);
    // console.log(depict_url)
    img.attr('src', sw_server + depict_url.substring(1) + '&' + $.param(extra));
    img.attr('onmouseenter', 'show_imgpop(this);');
    img.attr('onmouseleave', 'hide_imgpop();');
    img.attr('ondragstart', 'drag_img(event, "' + data.hitSmiles + '");');
    var div = $("<div></div>");
    var id = datasets[search_state.db].prefix + data.id;
    var href = datasets[search_state.db].url.replace("%s", data.id);
    button.attr('id', id);
    button.attr('data-identifier', id);
    button.attr('data-db', search_state.db);
    button.attr('data-hg', false);
    button.attr('data-img', sw_server + depict_url.substring(1) + '&' + $.param(extra));
    button.attr('onclick', 'toggleCart(this)');
    button.attr('class', 'btn btn-info');
    let cart = JSON.parse(localStorage.getItem('cart'))
    let items = []
    for (i = 0; i < cart.length; i++) {
        items.push(cart[i].identifier)
    }
    if (items.includes(id)) {
        button.html('Remove')
        button.attr('class', 'btn btn-danger')
    }
    if (href) {
        div.append("<b><a target='_blank' href='" + href + "'>" + id + "</a></b>");
    } else {
        //div.append("<b><a target='_blank' href='http://zinc15.docking.org/substances/"+id+"'>" + id + "</a></b>");
        var checkZinc = id.toString()
        if (checkZinc.substring(0, 4) == 'ZINC') {
            div.append("<b><a target='_blank' href='https://zinc15.docking.org/substances/" + id + "'>" + id + "</a></b>");
        } else {
            div.append("<b>" + id + "</b>");
        }
    }
    var $props = $('<div>').append('<b>SWIDX:</b>' + data.anonIdx)
        .append('<br/><b>MW:</b> ' + data.mw)
        .append('<br/><b>MF:</b> ' + data.mf);
    $props.css('font-size', 'smaller');
    div.append($props);
    var row = $('<tr></tr>');
    row.append($("<td style='width: 50px; margin:50px;'></td>").append(button));
    row.append($("<td style='width: 150px;'></td>").append(img));
    row.append($("<td style='line-height: 100%;'></td>").append(div));
    table.append(row);

    return $('<div>').append(table).html();
}


// function toggleCart(btn) {
// 	if (btn.getAttribute('class') == 'btn btn-info') {
// 		$.ajax({
// 			type: 'POST',
// 			url: '/addToCart',
// 			data: JSON.stringify({
// 				'id': btn.id,
// 				'database': btn.getAttribute('db'),
// 				'img_url': btn.getAttribute('img')
// 			}),
// 			contentType: "application/json; charset=utf-8",
// 			dataType: "json",
// 			success: function (result) {
// 				$(btn).html('Remove')
// 				$(btn).attr('class', 'btn btn-danger')
// 				if (!items.includes(btn.id)) {
// 					items.push(btn.id)
// 				}
// 				$('#cartCount').html(result['count'])
// 				$.ajax({
// 					type: 'POST',
// 					url: '/autoChooseVendor/' + result['item_id'],
// 					contentType: "application/json; charset=utf-8",
// 					dataType: "json",
// 				})
// 			},
// 			error: function (data) {
// 				alert("fail");
// 			}
// 		});
// 	}
// 	else {
// 		$.ajax({
// 			url: '/deleteItem/' + btn.id,
// 			type: 'DELETE',
// 			success: function (result) {
// 				$(btn).html('Add To Cart')
// 				$(btn).attr('class', 'btn btn-info')
// 				items.pop(btn.id)
// 				$('#cartCount').html(result['count'])
// 			}
// 		});
//
// 	}
//
//
//
// 	return false;
// }