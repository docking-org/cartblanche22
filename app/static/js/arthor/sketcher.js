var sketcher = 'jsme'; // jsme marvinjs

var marvinjs = null;
var jsmeApplet = null;
var fromSmiInput = false;
var sketchCallback = null;
var prevTextInput = null;

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
  if (sketcher == "jsme") {
    jsmeApplet = new JSApplet.JSME("sketcher", "420px", "300px", {
      "options": "newlook,nocanonize"
    });
    jsmeApplet.setAfterStructureModifiedCallback(function (event) {
      var smiles = event.src.smiles();
      if (localStorage)
        localStorage.molfile = event.src.molFile();
      if (smiles === "")
        return;
      if (sketchCallback)
        sketchCallback(smiles);
      if (!fromSmiInput) {
        prevTextInput = null;
        $('#smiles-in').val(smiles);
        console.log('jsmeOnLoad')
      }
    });
  }
}

function set_smiles(callback) {
  if (sketcher == 'jsme') {
    fromSmiInput = true;
    callback(jsmeApplet.smiles());
    fromSmiInput = false;
  } else if (sketcher == 'marvinjs') {
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
                      console.log('set_smiles')

            }
            fromSmiInput = false;
          });
      }, function (error) {
        alert("Molecule export failed:" + error);
      });
  }
}

function set_structure(molfile) {
  if (fromSmiInput) return;
  if (!molfile) {
    if (sketcher == 'jsme') {
      if (jsmeApplet) {
        jsmeApplet.clear();
        jsmeApplet.repaint();
      }
    } else {
      marvinjs.clear();
    }
    prevTextInput = null;
    return;
  }
  if (sketcher == 'jsme') {
    fromSmiInput = true;
    jsmeApplet.readMolFile(molfile);
    fromSmiInput = false;
  } else if (sketcher == 'marvinjs') {
    fromSmiInput = true;
    marvinjs.importStructure("mol", molfile);
    fromSmiInput = false;
  }
}

function resolve_structure(input) {
  if (fromSmiInput) return;

  var smi = $(input).val();
  if (smi === prevTextInput)
    return;
  prevTextInput = smi;
  if (!smi)
    return;
  var url = arthor.config.WebApp.RESOLVER;
  console.log('ftom resolve: ' + url)
  url = url.replace("%s", encodeURIComponent(smi));
  $.get(url).then(function (molfile) {
    if (molfile)
      set_structure(molfile);
  })
    .fail(function (fail) {
      add_at_mesg("Could not resolve structure from text: '" + smi + "'",
        Mesg.Info);
    });
}

function load_smiles(input) {
  console.log('zurj chadahnuu haray l da')
  if (fromSmiInput) return;
  var smi = $(input).val();
  var url = 'http://sw.docking.org/util/smi2mol?smi=%s'


  url = url.replace("%s", encodeURIComponent(smi));
  console.log(url)
  $.get(url,
    function (res) {
      if (res) {
        if (sketcher == 'jsme') {
          console.log(res)
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

