function MouseOver(id) {
  this.id   = id;
  this.$div = null;
  this.xOffset = 10;
  this.yOffset = -200;

  $(document).ready(
    (function(mouseover) {
      return function(){
        mouseover.$div = $('<div>').attr('id', id);
        $('body').append(mouseover.$div);
      };})(this));

  this.show = function(url, x, y) {
    this.$div.html($('<img>').attr('src', url));
    this.$div.css('z-index', '999999')
             .css('background', 'white')
             .css('display', 'block')
             .css('position', 'absolute')
             .css('top', y+this.yOffset)
             .css('left', x+this.xOffset);
  };

  this.move = function(x, y) {
    this.$div.css('position', 'absolute')
             .css('top', y+this.yOffset)
             .css('left', x+this.xOffset);
  };

  this.hide = function(x, y) {
    this.$div.css('display', 'none');
  };
}