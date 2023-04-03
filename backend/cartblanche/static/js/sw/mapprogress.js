function new_premapbar(key, progress, w, h) {
	 var $svg  = $(document.createElementNS("http://www.w3.org/2000/svg", "svg")).addClass('yielddohnut');
   var chart = d3.selectAll($svg.toArray())
                 .attr('width',  w)
                 .attr('height', h);

   x_scale = d3.scaleLinear().range([0, w]);
   x_scale.domain([0, 1]);

   chart.append("rect").attr("x", 0)
      	 .attr("y", 0)
         .attr("height", h)
         .attr("width", x_scale(progress))
         .attr("fill", '#7cadff')

   return $svg;
}

function new_progressbar(key, numMapped, numUnmapped, numSkipped, total, h) {

	var $tip = $('#progress-bar-tooltip');
	if ($tip.length == 0) {
		$tip = $('<div id="progress-bar-tooltip">')
		$(document.body).append($tip);
	}

    var subtotal = numMapped + numUnmapped;

    if (key == $tip.data('key')) {
        if (subtotal !== total) {
            $tip.html(
                    '<table>' +
                        '<tr>' +
                          '<td>Progress</td><td>' + new Number(100*subtotal/total).toFixed(2) + '%</td><td>' + subtotal.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                         '</tr><tr>' +
                            '<td>Mapped</td><td>' + new Number(100*numMapped/subtotal).toFixed(2) + '%</td><td>' + numMapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                        '</tr><tr>' +
                            '<td>Unmapped</td><td>' + new Number(100*numUnmapped/subtotal).toFixed(2) + '%</td><td>' + numUnmapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                        '</tr>' +
                    '</table>'
                  );
        } else {
            $tip.html(
                    '<table>' +
                        '<tr>' +
                            '<td>Mapped</td><td>' + new Number(100*numMapped/subtotal).toFixed(2) + '%</td><td>' + numMapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                        '</tr><tr>' +
                            '<td>Unmapped</td><td>' + new Number(100*numUnmapped/subtotal).toFixed(2) + '%</td><td>' + numUnmapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                        '</tr>' +
                    '</table>'
                  );
        }
	}


  var $svg  = $(document.createElementNS("http://www.w3.org/2000/svg", "svg")).addClass('progressbar');
  var chart = d3.selectAll($svg.toArray())
                .attr('width',  '100%')
                .attr('height', h);


  x_scale = d3.scaleLinear().range([0, 100]);
  x_scale.domain([0, subtotal]);

  sub_scale = d3.scaleLinear().range([0, x_scale(subtotal)]);
  sub_scale.domain([0, total]);

	chart.append("rect").attr("x", 0)
   		.attr("y", 0)
      .attr("height", h)
      .attr("width", sub_scale(numMapped) + '%')
      .attr("fill", '#3bffa1')
  chart.append("rect")
  	  .attr("x", sub_scale(numMapped) + '%')
   		.attr("y", 0)
      .attr("height", h)
      .attr("width", sub_scale(numUnmapped) + '%')
      .attr("fill", '#ff4a1f')
	chart.on('mouseover', function(e){
					var coordinates = d3.mouse(chart.node());
          var x = coordinates[0];
          var y = coordinates[1];
          if (subtotal !== total) {
              $tip.html(
                      '<table>' +
                          '<tr>' +
                            '<td>Progress</td><td>' + new Number(100*subtotal/total).toFixed(2) + '%</td><td>' + subtotal.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                           '</tr><tr>' +
                              '<td>Mapped</td><td>' + new Number(100*numMapped/subtotal).toFixed(2) + '%</td><td>' + numMapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                          '</tr><tr>' +
                              '<td>Unmapped</td><td>' + new Number(100*numUnmapped/subtotal).toFixed(2) + '%</td><td>' + numUnmapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                          '</tr>' +
                      '</table>'
                    );
          } else {
              $tip.html(
                      '<table>' +
                          '<tr>' +
                              '<td>Mapped</td><td>' + new Number(100*numMapped/subtotal).toFixed(2) + '%</td><td>' + numMapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                          '</tr><tr>' +
                              '<td>Unmapped</td><td>' + new Number(100*numUnmapped/subtotal).toFixed(2) + '%</td><td>' + numUnmapped.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '</td>' +
                          '</tr>' +
                      '</table>'
                    );
          }
					$tip.css('left', $svg.offset().left + x + 'px');
          $tip.css('top',  $svg.offset().top - $tip.outerHeight() + 'px');
          $tip.data('key', key);
					$tip.show();
				})
				.on('mousemove', function(e){
        					var coordinates = d3.mouse(chart.node());
                  var x = coordinates[0];
                  var y = coordinates[1];
        					$tip.css('left', $svg.offset().left + x - 25 + 'px');
          				$tip.css('top',  $svg.offset().top - $tip.outerHeight() - 8 + 'px');
        				})
       .on('mouseout', function(e){
					$tip.hide();
       })

  return $svg;
}