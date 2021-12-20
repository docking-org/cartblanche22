function make_add_box() {
  var $box = $('<div id="add-new" class="arthor_table_box static">');
  var $top = $('<table class="arthor_table_top">');
  var $bot = $('<table class="arthor_table_bottom">');

  var $addButton     = $('<i class="fa fa-plus" aria-hidden="true"></i>');
  var $nameInput     = $('<input name="name" type="text" placeholder="New Dataset...">');

  $addButton.css('cursor', 'pointer');

  $addButton.click(function($box){
      var $nameinput = $('input[name=name]', $box);
      var $fileinput = $('input[type=file]', $box);

      var name = $nameinput.val();

      var tFlash = 250;
      var okay  = true;

      // check fileinput
      if(!$fileinput.val()) {
          $fileinput.stop().fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash);
          okay = false;
      }

      if (name.length == 0) {
          $nameinput.focus();
          $nameinput.stop().fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash).fadeOut(tFlash).fadeIn(tFlash);
          okay = false;
      }

      if (okay) {
          var formData = new FormData($('form', $box)[0]);
          var $add     = $('#add-new');
          var fade     = setInterval((function($elem){
                                          $elem.fadeTo(800, 0.5).fadeTo(800, 1);
                                      }).bind(null, $add), 1600);
          $.ajax({
              url: arthor.url + '/dt/upload',
              type: 'POST',
              data: formData,
              cache: false,
              contentType: false,
              processData: false
          }).done(function(returndata) {
            clearInterval(fade);
            reload();
          });
      }
  }.bind(null, $box));

  // tooltips
  $addButton.attr('title', 'Add a new dataset');

  $top.append($('<tr>').append($('<td>').append('<i class="fa fa-database" aria-hidden="true"></i>'))
                       .append($('<td>').append($nameInput))
                       .append($('<td>').append($addButton)));

  var $fileInput = $('<input name="file" type="file">');
  var $urlInput = $('<input name="url" type="text">').attr('placeholder', '...');

  $bot.append($('<tr>').append($('<td>').attr('colspan', 2).append($fileInput)));
  $bot.append($('<tr>').append($('<td>').append('Identifier URL'))
                       .append($('<td>').append($urlInput)));

  $box.append($('<div>').append($('<form>').append($top, $bot)));
  return $box;
}

function plotmem(count) {
  var boxes = [];
  var max = (count / 1000) * 40;
  for (var i = 0; i < 40; i++) {
    if (i < max)
      boxes.push('<div class="mempage_outer paged_in"><div class="mempage_inner"></div></div>');
    else
      boxes.push('<div class="mempage_outer"><div class="mempage_inner"></div></div>');
  }
  return boxes;
}

function meminfo(title, table, itype, count) {
  var parts = [];
  var $touch_but = $('<button>').attr('title', 'Paging memory in')
                                .append('<i class="fa fa-bolt"></i> Touch');
  var $evict_but = $('<button>').attr('title', 'Suggest paging memory out, hint only')
                                .append('<i class="fa fa-eject"></i> Evict');
  $touch_but.click(function(){
    arthor.memtouch(table, itype);
  });
  $evict_but.click(function(){
    arthor.memevict(table, itype);
  });
  var $inner = $('<div></div>').append(title);
  if (count < 900)
    $inner.append(' ').append($touch_but);
  if (count > 0)
    $inner.append(' ').append($evict_but);
  parts.push($inner);
  parts.push($('<div class="memplot">').attr('title', 100*(count/1000) + '% in vmemory').append(plotmem(count)));
  return parts;
}

function reload() {
arthor.getTables()
      .done(function(response) {
          var $list = $('#arthor_tables');
          $list.empty();
          $.each(response, function(i,e) {
              var $box = $('<div>').addClass('arthor_table_box');
              var $top = $('<table>').addClass('arthor_table_top');
              var $bot = $('<table>').addClass('arthor_table_bottom');

              var $url = $('<input type="text">').attr('placeholder', '...');
              if (e.urlFormatStr)
                $url.attr('value', e.urlFormatStr);

              $top.append($('<tr>').append($('<td>').append('<i class="fa fa-database" aria-hidden="true"></i>&nbsp;').append(e.displayName)));
              $bot.append($('<tr>').append($('<td>').append('Location'))
                                   .append($('<td>').append(e.location)));
              $bot.append($('<tr>').append($('<td>').append('Identifier URL'))
                                   .append($('<td>').append($url)));
              var $meminfo = $('<div class="meminfo">');
              $meminfo.append('<div>Substructure Index</div>');
              $meminfo.append('<i class="fa fa-spinner fa-pulse"></i>');
              $meminfo.append('<div>Similarity Index</div>');
              $meminfo.append('<i class="fa fa-spinner fa-pulse"></i>');
              $box.append($('<div>').append($top, $bot, $meminfo));
              $list.append($box);
              arthor.meminfo(e.displayName).done(function(res){
                $meminfo = $box.find('.meminfo');
                $meminfo.empty();
                $meminfo.append(meminfo('Substructure Index', e.displayName, 'SUB', res['SUB']));
                $meminfo.append(meminfo('Similarity Index', e.displayName, 'SIM', res['SIM']));
              });
          });
          $list.append(make_add_box());
        });
}

$(document).ready(function(){
reload();
});