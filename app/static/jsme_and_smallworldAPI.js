//Initial parameters to call SmallWorld API. These will be updated when changes are made in the molecule editor

var sw_parameters = {
    smiles: 'c1ccccc1',
    db: 'ZINC-Interesting-297K',
    dist: 4,
    tdn: 4,
    tup: 4,
    rdn: 4,
    rup: 4,
    ldn: 4,
    lup: 4,
    maj: 4,
    min: 4,
    sub: 4
};
const sw_server = 'http://sw.docking.org'
let hlid;
let sw_response;
let split_hlid_string;
let clean_split_string = [];
let first_data_string;
let parsed_response_obj = {};
let sw_view = String();
let source = false;
let datasets = [];
let dtable = null;

//this function will be called after the JavaScriptApplet code has been loaded.
function jsmeOnLoad() {
    jsmeApplet = new JSApplet.JSME("sketcher", "420px", "300px");
    document.JME = jsmeApplet;
    jsmeApplet.setAfterStructureModifiedCallback(function (event) {
        console.log('from setaAFter')
        getSmiles()
    });
}

function readMolecule() {
    var jme = "16 17 C 7.37 -8.99 C 7.37 -7.59 C 6.16 -6.89 C 4.95 -7.59 C 4.95 -8.99 C 6.16 -9.69 N 8.58 -6.89 C 8.58 -5.49 C 7.37 -4.79 O 6.16 -5.49 C 9.80 -7.59 O 9.80 -8.99 C 11.01 -6.89 Cl 12.22 -7.59 Cl 11.01 -5.49 C 9.80 -4.79 1 2 1 2 3 2 3 4 1 4 5 2 5 6 1 6 1 2 7 8 1 8 9 1 9 10 1 3 10 1 2 7 1 7 11 1 11 12 2 11 13 1 13 14 1 13 15 1 8 16 1";
    jsmeApplet.readMolecule(jme); // or document.JME.readMolecule(jme);
}

function readMultipart() {
    var jme = "9 9 C 6.68 -7.15 C 5.47 -6.45 C 4.26 -7.15 C 4.26 -8.55 C 5.47 -9.25 C 6.68 -8.55 C 5.47 -5.05 O- 6.68 -4.35 O 4.26 -4.35 1 2 1 2 3 2 3 4 1 4 5 2 5 6 1 6 1 2 2 7 1 7 8 1 7 9 2|1 0 Na+ 12.21 -6.61";
    jsmeApplet.readMolecule(jme); // or document.JME.readMolecule(jme
}

function readReaction() {
    var jme = "3 2 C:1 1.41 -7.12 O:2 1.41 -5.72 Cl 2.63 -7.82 1 2 2 1 3 1|3 2 N:3 5.72 -6.78 C:4 7.12 -6.78 H:5 5.02 -7.99 1 2 1 1 3 1 >> 5 4 C:1 13.51 -6.40 O:2 13.51 -5.00 N:3 14.72 -7.10 C:4 15.94 -6.40 H:5 14.71 -8.50 1 2 2 1 3 1 3 4 1 3 5 1";
    jsmeApplet.readMolecule(jme);
}


function getMolfile(isV3000) {
    var data = document.JME.molFile(isV3000);
    document.getElementById("jme_output").value = data;

}

function getSmiles() {
    var data = document.JME.smiles();
    document.getElementById("smiles-in").value = data;
    sw_parameters["smiles"] = data;
    console.log(sw_parameters);
}

function getJMEstring() {
    var data = document.JME.jmeFile();
    document.getElementById("jme_output").value = data;
}

function readMoleculeFromTextArea() {
    var jme = document.getElementById("jme_output").value;
    jsmeApplet.readMolecule(jme);
}

function readMOLFromTextArea() {
    var mol = document.getElementById("jme_output").value;
    jsmeApplet.readMolFile(mol);
}

function readAnyFromTextArea() {
    var mol = document.getElementById("jme_output").value;
    jsmeApplet.readGenericMolecularInput(mol);
}

function stopStreaming() {
    if (source) source.close();
}

function redraw() {
    if (!dtable)
        return;
    if ($('#results').dataTable().fnSettings() && $('#results').dataTable().fnSettings().oScroller) {
        var s = $('#results').dataTable().fnSettings().oScroller.s;
        s.dt.oApi._fnDraw(s.dt);
    } else {
        dtable.draw('full-hold');
    }
}

function callSmallWorld() {
    console.log("in function callSmallWorld()");
    var sw_url = 'http://sw.docking.org/search/submit?smi='.concat(String(sw_parameters["smiles"]), '&db=', String(sw_parameters["db"]), '&dist=', String(sw_parameters["dist"]), '&tdn=', String(sw_parameters["tdn"]), '&tup=', String(sw_parameters["tup"]), '&rdn=', String(sw_parameters["rdn"]), '&rup=', String(sw_parameters["rup"]), '&ldn=', String(sw_parameters["ldn"]), '&lup=', String(sw_parameters["lup"]), '&maj=', String(sw_parameters["maj"]), '&min=', String(sw_parameters["min"]), '&sub=', String(sw_parameters["sub"]), '&scores=Atom%20Alignment,ECFP4,Daylight%27');
    console.log(sw_url);

    source = new EventSource(sw_url);

    source.addEventListener('message', function (e) {
        var d = JSON.parse(e.data);
        if (d.status === "END") {
            console.log("end")
            // redraw();
            stopStreaming();
            // $('#statusspan').html("Finished (" + format_search_stats(d) + ")");
        } else {
            if (d.status === "FIRST") {
                console.log("from first " + d.hlid)
                hlid = d.hlid
                console.log(hlid + 'just checking')
                sw_view = 'http://sw.docking.org/search/view?hlid='.concat(String(hlid), '&columns%5B0%5D%5Bname%5D=alignment&start=1&length=5&draw=1');
                console.log(typeof sw_view)

                // init_table($('#results'), sw_view);
                // $('.dataTables_scrollBody').css('background', 'repeating-linear-gradient(45deg, #edeeff, #edeeff 10px, #fff 10px, #fff 20px)');
                // let url = sw_server + '/search/view/?hlid=' + d.hlid;

                // $('#statusspan').html("Searching... (" + format_search_stats(d) + ")");
                // var url = sw_server + '/search/view/?hlid=' + d.hlid;
                // init_table($('#results'), url);
                // $('.dataTables_scrollBody').css('background', 'repeating-linear-gradient(45deg, #edeeff, #edeeff 10px, #fff 10px, #fff 20px)');
            } else if (d.status === "MORE") {
                console.log("more searching--" + d)
                // $('#statusspan').html("Searching... (" + format_search_stats(d) + ")");
                // redraw();
            } else if (d.status === "MISS") {
                // $('#statusspan').html("Query not indexed");
                console.log("query not indexed")
                stopStreaming();
                // $('.dataTables_scrollBody').css('background', 'repeating-linear-gradient(45deg, #ffcbaf, #ffcbaf 10px, #fff 10px, #fff 20px)');
            } else {
                console.log("searching--" + d)
                // $('#statusspan').html("Searching... (" + format_search_stats(d) + ")");
                // ping to check if we're still listening?
            }
        }
    }, false);
}

function callSWView() {
    console.log('In callSWView function');
    sw_view = 'http://sw.docking.org/search/view?hlid='.concat(String(hlid), '&columns%5B0%5D%5Bname%5D=alignment&start=1&length=5&draw=1');
    console.log(sw_view);
    var getJSON = function (url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'application/json';
        xhr.onload = function () {
            var status = xhr.status;
            if (status === 200) {
                callback(null, xhr.response);
            } else {
                callback(status, xhr.response);
            }
        };
        xhr.send();
    };
    getJSON(sw_view, function (err, data) {
        if (err != null) {
            alert('Something went wrong: ' + err);
        } else {
            alert('Called SmallWorld View!');
            console.log(data);
            // $(document).ready(function () {
            //     $('#myTable').DataTable();
            // });
        }
    });
}

function callSWExport() {
    console.log('In callSWExport function');
    sw_export = 'http://sw.docking.org/search/export?hlid='.concat(String(hlid), '&columns%5B0%5D%5Bname%5D=alignment&start=1&length=5&draw=1');
    console.log(sw_export);
    var getJSON = function (url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'application/json';
        xhr.onload = function () {
            var status = xhr.status;
            if (status === 200) {
                callback(null, xhr.response);
            } else {
                callback(status, xhr.response);
            }
        };
        xhr.send();
    };
    getJSON(sw_export, function (err, data) {
        if (err != null) {
            alert('Something went wrong: ' + err);
        } else {
            alert('Called SmallWorld Export!');
            console.log(typeof data);

        }
    });
}

function callSWMaps() {
    console.log('In callSWMap function');
    sw_map_url = 'http://sw.docking.org/search/maps';
    console.log(sw_map_url);
    var getJSON = function (url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'application/json';
        xhr.onload = function () {
            var status = xhr.status;
            if (status === 200) {
                callback(null, xhr.response);
            } else {
                callback(status, xhr.response);
            }
        };
        xhr.send();
    };
    getJSON(sw_map_url, function (err, data) {
        if (err != null) {
            alert('Something went wrong: ' + err);
        } else {
            alert('Called SmallWorld Map!');
            console.log(data);
        }
    });
}

function callSWConfig() {
    console.log('In callSWMap function');
    sw_config_url = 'http://sw.docking.org/search/config';
    console.log(sw_config_url);
    var getJSON = function (url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'application/json';
        xhr.onload = function () {
            var status = xhr.status;
            if (status === 200) {
                callback(null, xhr.response);
            } else {
                callback(status, xhr.response);
            }
        };
        xhr.send();
    };
    getJSON(sw_config_url, function (err, data) {
        if (err != null) {
            alert('Something went wrong: ' + err);
        } else {
            alert('Called SmallWorld Config!');
            console.log(data);
        }
    });
}

function recoverStorage() {
    var recover_initial_request = localStorage.getItem('_string_initial_request');
    recover_initial_request = atob(recover_initial_request);
    recover_initial_request = JSON.parse(recover_initial_request);
    console.log('Recover Initial Request');
    console.log(recover_initial_request);
}