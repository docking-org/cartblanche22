let sw_server = 'http://sw.docking.org'
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
function callSmallWorld(smile) {
    let sw_url = 'http://sw.docking.org/search/submit?smi='.concat(
        String(smile),
        '&db=', String(sw_parameters["db"]),
        '&dist=', String(sw_parameters["dist"]),
        '&tdn=', String(sw_parameters["tdn"]),
        '&tup=', String(sw_parameters["tup"]),
        '&rdn=', String(sw_parameters["rdn"]),
        '&rup=', String(sw_parameters["rup"]),
        '&ldn=', String(sw_parameters["ldn"]),
        '&lup=', String(sw_parameters["lup"]),
        '&maj=', String(sw_parameters["maj"]),
        '&min=', String(sw_parameters["min"]),
        '&sub=', String(sw_parameters["sub"]),
        '&scores=Atom%20Alignment,ECFP4,Daylight%27');

    console.log(sw_url);

    source = new EventSource(sw_url);

    source.addEventListener('message', function (e) {
        let d = JSON.parse(e.data);
        if (d.status === "END") {
            console.log("end")
            stopStreaming();
        } else {
            if (d.status === "FIRST") {
                console.log("found hlid" + d.hlid)
                hlid = d.hlid
                sw_view = 'http://sw.docking.org/search/view?hlid='.concat(String(hlid), '&columns%5B0%5D%5Bname%5D=alignment&start=1&length=1000&draw=0');
                loadData(sw_view);
            } else if (d.status === "MORE") {
                console.log("more searching--" + d)
            } else if (d.status === "MISS") {
                console.log("query not indexed")
                stopStreaming();
            } else {
                console.log("searching--" + d)
            }
        }
    }, false);
}

function stopStreaming() {
    if (source) {
        source.close();
    }
}
