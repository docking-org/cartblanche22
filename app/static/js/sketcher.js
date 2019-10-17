var sketcher = 'jsme'; // jsme marvinjs

var jsmeApplet = null;
var marvinjs = null;
var fromSmiInput = false;

// MarvinJS
$(document).ready(function (e) {
	if (sketcher == "marvinjs") {
		MarvinJSUtil.getEditor("#sketch-frame").then(function (sketcherInstance) {
			marvinjs = sketcherInstance;
			installSmallWorldCallback(marvinjs);

			var $canvas = $("#sketch-frame").contents().find('canvas');

			$canvas.on('dragover', function (event) {
				event.preventDefault();
			});

			$canvas.on('drop', function (event) {
				event.preventDefault();
				var molfile = event.originalEvent.dataTransfer.getData("text")
				fromSmiInput = true;
				marvinjs.importStructure("mol", molfile);
			});

		}, function (error) {
			alert("Loading of the sketcher failed" + error);
		});
	}
})


function jsmeOnLoad() {
	console.log("jsmeOnLoad")
	if (sketcher == "jsme") {
		jsmeApplet = new JSApplet.JSME("sketcher", "420px", "300px", {
			"options": "newlook"
		});
		jsmeApplet.setAfterStructureModifiedCallback(function (event) {
			var smiles = event.src.smiles();
			if (smiles === "")
				return;
			molChanged(smiles);
			if (!fromSmiInput) {
				$('#smiles-in').val(smiles);
			}
		});
	}
}

function set_smiles(callback) {
	if (sketcher == 'jsme') {
		fromSmiInput = true;
		if (jsmeApplet)
			callback(jsmeApplet.smiles());
		fromSmiInput = false;
	} else if (sketcher == 'marvinjs') {
		if (!marvinjs)
			return;
		marvinjs.exportStructure("mol")
			.then(function (molfile) {
				$.get(sw_server + '/util/mol2smi',
					{ molfile: molfile },
					function (res) {
						var smiles = res.smi;
						if (smiles === "")
							return;
						callback(smiles);
						if (!fromSmiInput) {
							$('#smiles-in').val(smiles);
						}
						fromSmiInput = false;
					});
			}, function (error) {
				alert("Molecule export failed:" + error);
			});
	}
}

function installSmallWorldCallback(marvinjs) {
	marvinjs.on('molchange', function () { set_smiles(molChanged) });
}

function load_smiles(input) {
	if (fromSmiInput) return;
	var smi = $(input).val();
	var url = config.WebApp.ResolverUrl;
	url = url.replace("%s", encodeURIComponent(smi));
	$.get(url,
		function (res) {
			if (res) {
				if (sketcher == 'jsme') {
					fromSmiInput = true;
					jsmeApplet.readMolFile(res);
					fromSmiInput = false;
				} else if (sketcher == 'marvinjs') {
					fromSmiInput = true;
					marvinjs.importStructure("mol", res);
					fromSmiInput = false;
				}
			}
		});
}



