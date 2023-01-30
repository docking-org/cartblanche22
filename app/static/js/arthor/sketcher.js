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
    jsmeApplet = new JSApplet.JSME("sketcher", "420px", "500px", {
      "options": "newlook,nocanonize",
      "smiles": ""
    });
    jsmeApplet.setAfterStructureModifiedCallback(function (event) {
      var smiles = event.src.smiles();
      if (localStorage)
        localStorage.molfile = event.src.molFile();

      if (sketchCallback)
        sketchCallback(smiles);

      prevTextInput = null;

      $('#smiles-in').val(smiles);

    });

    jsmeApplet.setCallBack("AfterPaste", (function (event) {
      var smiles = event.src.smiles();
      $('#smiles-in').val(smiles);
      sketchCallback(smiles);
    }));
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

            callback(smiles);

            $('#smiles-in').val(smiles);


            fromSmiInput = false;
          });
      }, function (error) {
        alert("Molecule export failed:" + error);
      });
  }
}

function set_structure(molfile) {

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
    ;
    jsmeApplet.readMolFile(molfile);
    $.get('https://sw.docking.org/util/mol2smi',
          { molfile: molfile },

          function (res) {
            var smiles = res.smi;

            

            $('#smiles-in').val(smiles);


          });

    fromSmiInput = false;
  } else if (sketcher == 'marvinjs') {
    fromSmiInput = true;
    marvinjs.importStructure("mol", molfile);
    fromSmiInput = false;
  }
}

function resolve_structure(input) {

  var smi = $(input).val();
  if (smi === prevTextInput)
    return;
  prevTextInput = smi;
  if (!smi)
    return;
  var url = arthor.config.WebApp.RESOLVER;
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
  console.log('load smiles')

  var smi = $(input).val();
  var url = 'https://sw.docking.org/util/smi2mol?smi=%s'


  url = url.replace("%s", encodeURIComponent(smi));
  $.get(url,
    function (res) {
      if (res) {
        if (sketcher == 'jsme') {
          fromSmiInput = true;
          jsmeApplet.readMolFile(res);
         
          sketchCallback(smi);
          fromSmiInput = false;
        } else if (sketcher == 'marvinjs') {
          fromSmiInput = true;
          marvinjs.importStructure("mol", res);
          fromSmiInput = false;
        }
      }
    });
}

