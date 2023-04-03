var sketcher = 'jsme'; // jsme marvinjs

var jsmeApplet = null;
var marvinjs = null;
var fromSmiInput = true;

function jsmeOnLoad() {
	console.log('jsmeOnLoad');

	if (sketcher == "jsme") {
		jsmeApplet = new JSApplet.JSME("sketcher", "420px", "500px", {
			"options": "newlook",
			"smiles": document.getElementById("smiles-in").value
		});
		jsmeApplet.setCallBack("AfterStructureModified", (function (event) {
			var smiles = event.src.smiles();

			$('#smiles-in').val(smiles);
			molChanged(smiles);
		}));

		jsmeApplet.setCallBack("AfterPaste", (function (event) {
			var smiles = event.src.smiles();
			$('#smiles-in').val(smiles);
			molChanged(smiles);
		}));
	}

}

function set_smiles(callback) {

	if (sketcher == 'jsme') {

		if (jsmeApplet) {
			callback(jsmeApplet.smiles());
		}

	} else if (sketcher == 'marvinjs') {
		if (!marvinjs)
			return;
		marvinjs.exportStructure("mol")
			.then(function (molfile) {
				$.get(sw_server + '/util/mol2smi',
					{ molfile: molfile },
					function (res) {
						var smiles = res.smi;

						callback(smiles);

						$('#smiles-in').val(smiles);


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

	var smi = $(input).val();
	var url = config.WebApp.ResolverUrl;
	url = 'https://sw.docking.org/' + url.substring(2)
	url = url.replace("%s", encodeURIComponent(smi));
	$.get(url,
		function (res) {
			console.log(url)
			if (res) {
				molChanged(smi);
				if (sketcher == 'jsme') {

					jsmeApplet.readMolFile(res);
				}
				else if (sketcher == 'marvinjs') {

					marvinjs.importStructure("mol", res);

				}
			}
		});
}



