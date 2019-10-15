function jsmeOnLoad() {
    jsmeApplet = new JSApplet.JSME("jsme_container", "380px", "340px");
    document.JME = jsmeApplet;
    jsmeApplet.setAfterStructureModifiedCallback(function (event) {
        getSmiles()
    });
}


function getSmiles() {
    let data = document.JME.smiles();
    document.getElementById("smiles-in").value = data;
    callSmallWorld(data)
}