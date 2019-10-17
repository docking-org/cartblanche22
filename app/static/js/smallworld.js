var source = false;

var datasets     = {};
var dtable       = null;
var search_state = null;

function load_smiles(input) {
    var smi = $(input).val();
    $.get('../util/smi2mol',
          {smi: smi},
          function (res) {
            if (res && res.smi === smi) {
                jsmeApplet.readMolFile(res.mol);
            }
          });
}
function install_range_slider(param, limit) {
    if (!limit) {
        limit = 15;
    }
    var lb = $("input[name='" + param + "lb']");
    var ub = $("input[name='" + param + "ub']");
    var range = $('#' + param + 'slider').slider({min: 0,
                                                  max: limit,
                                                  range: true,
                                                  values: [0, 10],
                                                  slide: function( event, ui ) {
                                                          lb.val(ui.values[0]);
                                                          ub.val(ui.values[1]);
                                                          update_bound(param, false);
                                                        }});

    lb.val(0);
    ub.val(10);
    lb.prop('readonly', true);
    ub.prop('readonly', true);
    lb.css('background-color', 'transparent');
    ub.css('background-color', 'transparent');
    lb.css('background-color', 'transparent');
    lb.css('border', 'none');
    ub.css('border', 'none');
    lb.change(function() {
        range.slider('values', 0, lb.val());
        range.slider('values', 1, ub.val());
    });
    ub.change(function() {
        range.slider('values', 0, lb.val());
        range.slider('values', 1, ub.val());
    });
}

function jsmeOnLoad() {
	jsmeApplet = new JSApplet.JSME("jsme_container", "380px", "320px", {
	   "options" : "newlook,query"
	});
	jsmeApplet.setAfterStructureModifiedCallback(function(event) {
	    var smiles = event.src.smiles();
        if (smiles === "")
          return;
        startStreaming(smiles);
	});
}

function set_mode() {
    var val = $("select[name='mode'] option:selected").val();
    if (val === 'swsub') {
      set_mode_sw_subsearch();
    }
    else if (val === 'swsup') {
      set_mode_sw_supsearch();
    }
    else if (val === 'swmcs') {
      set_mode_sw_mcssearch();
    }
    else if (val === 'swsim') {
      set_mode_sw_simsearch();
    }
    else if (val === 'swmurko') {
      set_mode_sw_murko();
    }
    else if (val === 'swskel') {
      set_mode_sw_skel();
    }
    update_bounds();
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


function db_maps(select) {
  $.get('../search/list_db_maps', function( data ) {
    for (var i in data) {
      datasets[data[i].name] = data[i];
      select.append('<option value=' + data[i].name + '>' + data[i].name + '</option>');
    }
  });
}

function refresh() {

  // restart search
  if (search_state != null && jsmeApplet.smiles()) {
    startStreaming(jsmeApplet.smiles());
  }
}

/*
 * Export the current table view.
 */
function export_results() {
  if (!dtable) {
    return;
  }
  var url   = dtable.ajax.url();
  var regex = /hlid=(\d+)/;
  var hlid  = regex.exec(url);

  var params = {
    hlid: hlid[1]
  };

  $.each(dtable.order(), function(i, val) {
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

  window.open('../search/export?' + $.param(params));
}

function startStreaming(smiles) {

  if (!!window.EventSource) {
    stopStreaming();

    // Store the search parameters
    search_state = {
        smi:  smiles,
        db:   $("select[name='db'] option:selected").text(),
        dist: $("input[name='distub']").val(),
        tdn:  $("input[name='tdnub']").val(),
        tup:  $("input[name='tupub']").val(),
        rdn:  $("input[name='rdnub']").val(),
        rup:  $("input[name='rupub']").val(),
        ldn:  $("input[name='ldnub']").val(),
        lup:  $("input[name='lupub']").val(),
        maj:  $("input[name='mahub']").val(),
        min:  $("input[name='minub']").val(),
        sub:  $("input[name='subub']").val(),
    };

    source = new EventSource('/search/sim?smi=' + encodeURIComponent(search_state.smi) +
                             '&db=' + encodeURIComponent(search_state.db) +
                             '&dist=' + search_state.dist +
                             '&tdn=' + search_state.tdn +
                             '&tup=' + search_state.tup +
                             '&rdn=' + search_state.rdn +
                             '&rup=' + search_state.rup +
                             '&ldn=' + search_state.ldn +
                             '&lup=' + search_state.lup +
                             '&maj=' + search_state.maj +
                             '&min=' + search_state.min +
                             '&sub=' + search_state.sub);
  } else {
    console.log("ERROR: Browser does not support server-sent events");
    $('#results').append('<tr><td>Browser does not support Server-Side Events!</td></tr>');
    return;
  }

  source.addEventListener('message', function(e) {
    var d = JSON.parse(e.data);
    if (d.status === "END") {
      stopStreaming();
      $('#statusmesg').html("Finished (" + d.elap + " Elapsed)");
    } else {
      if (d.status === "FIRST") {
        $('#statusmesg').html("Searching... (" + d.elap + " Elapsed)");
        init_table($('#results'), d.hlid);
      }
      else if (d.status === "MORE" ) {
        $('#statusmesg').html("Searching... (" + d.elap + " Elapsed)");
        redraw();
      } else {
        $('#statusmesg').html("Searching... (" + d.elap + " Elapsed)");
        // ping to check if we're still listening?
      }
    }
  }, false);

  source.addEventListener('error', function(e) {
    stopStreaming();
    redraw();
    $('#statusmesg').html("Finished (Timeout)");
  }, false);


}

function redraw() {
 if (!dtable) {
    return;
 }
 if ($('#results').dataTable().fnSettings().oScroller) {
    var s = $('#results').dataTable().fnSettings().oScroller.s;
    s.dt.oApi._fnDraw(s.dt);
 } else {
    dtable.draw('full-hold');
 }
}

function hide_imgpop() {
    $('#imgpop').hide();
}

function show_imgpop(img) {
    var popup = $('#imgpop');
    popup.empty();
    popup.append('<img width="300px" height="180px" src="' + img.src + '"/>');

    var offset = $(img).offset();

    popup.css('left', offset.left + 160 + 'px');
    popup.css('top',  offset.top  - 50 + 'px');

    popup.show();
}

function stopStreaming() {
  if (source)
    source.close();
}

function init_table(table, hlid) {
if (dtable == null) {
  dtable = table.DataTable( {
    "columns": [
       { "title": "Compound",
         "name" : "compound",
         "class": "compound",
         "sortable": false,
         "type":  "html",
         "width": "250px",
         "render": compound_renderer,
       },
       { "title": "TDN",
         "name" : "tdn",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "TUP",
         "name" : "tup",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "RDN",
         "name" : "rdn",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "RUP",
         "name" : "rup",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "LDN",
         "name" : "ldn",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "LUP",
         "name" : "lup",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "MUT",
         "name" : "mut",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "MAJ",
         "name" : "maj",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "MIN",
         "name" : "min",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "SUB",
         "name" : "sub",
         "class": "editop",
         "width": "38px",
         "sortable": true,
         "searchable": true},
       { "title": "Distance",
         "name" : "dist",
         "width": "65px",
         "sortable": true},
       { "title": "ECFP4",
         "name" : "ecfp",
         "width": "50px",
         "sortable": true},
      ],
    destroy:     false,
    serverSide:  true,
    autoWidth:   false,
    filter:      true,
    "ajax": {
      "url": '/search/view/?hlid=' + hlid,
      "type": 'GET'
    },
    "dom": 'rtpi',
    "scrollX":     false,
    "scrollY":     (function() {
                       var height = table.height() - 70;
                       if (height < 50) {
                          return 800;
                       } else {
                          return height;
                       }
                   })(),
    "deferRender": true,
    "scroller": {
      "rowHeight":        92,
      "loadingIndicator": false,
      "serverWait":       20,
      "displayBuffer":    3
    },
  });

  update_bounds();

  } else {
    dtable.ajax.url('/search/view/?hlid=' + hlid).load();
  }
}

function update_bounds() {
  update_bound('dist', true);
  update_bound('tdn', true);
  update_bound('tup', true);
  update_bound('rdn', true);
  update_bound('rup', true);
  update_bound('ldn', true);
  update_bound('lup', true);
  update_bound('maj', true);
  update_bound('min', true);
  update_bound('sub', true);
  dtable.draw();
}

// Update the bound on a search parameter
function update_bound(param, nodraw) {
    update_bound_range(param,
                       $("input[name='" + param + "lb']").val(),
                       $("input[name='" + param + "ub']").val(),
                       nodraw);
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
    dtable.column(param + ":name")
          .search('');
  }
  else {
    dtable.column(param + ":name")
          .search(lb + "-" + ub);
  }

  if (!nodraw) {
    dtable.draw();
  }
}

function compound_renderer(data, type, row) {

   var table = $("<table class='compound_cell'></table>");

   var img = $('<img width="150px" height="90px" />');
   img.attr('src', '/search/depict/?w=50&h=30&hlid=' + data[0] + '&row=' + data[1]);
   img.attr('onmouseenter', 'show_imgpop(this);');
   img.attr('onmouseleave', 'hide_imgpop();');

   var div = $("<div></div>");

   var id   = datasets[search_state.db].prefix + data[2];
   var href = datasets[search_state.db].url.replace("%s", id);

   if (href) {
    div.append("<b><a target='_blank' href='" + href + "'>" + id + "</a></b>");
   } else {
    div.append("<b>" + id + "</b>");
   }
   div.append("<br/>");
   div.append('<b>MW:</b> ' + data[3]);
   div.append("<br/>");
   div.append('<b>MF:</b> ' + data[4]);

   var row = $('<tr></tr>');
   row.append($("<td style='width: 150px'></td>").append(img));
   row.append($("<td style='width: 100px; max-width: 100px;'></td>").append(div));
   table.append(row);

   return $('<div>').append(table)
                    .html();
}