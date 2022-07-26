var Mesg = {
  Info:  'info',
  Error: 'error'
};

var AutoHideInfoMesgTimeout = 4500;

function add_at_mesg(content, type) {
  var $mesg = $($('.at_mesgs .at_mesg')[0]);
  var $cpy = $mesg.clone();
  $cpy.find('.at_mesg_content').text(content);
  $cpy.addClass(type);
  // auto-hide info messages
  if (type === Mesg.Info) {
    setTimeout(function(){
      $cpy.fadeOut(1000);
    }, AutoHideInfoMesgTimeout);
  }
  $mesg.parent().append($cpy);
  $cpy.slideDown(200);
}