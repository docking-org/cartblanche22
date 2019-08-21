function getJSONP(url, success) {

    var ud = '_' + +new Date,
        script = document.createElement('script'),
        head = document.getElementsByTagName('head')[0] 
               || document.documentElement;

    window[ud] = function(data) {
        head.removeChild(script);
        success && success(data);
    };

    script.src = url.replace('callback=?', 'callback=' + ud);
    head.appendChild(script);

}

getJSONP('http://sw.docking.org//search/submit?smi=c1ccccc1&db=ZINC-Interesting-297K&dist=4&tdn=4&tup=4&rdn=4&rup=4&ldn=4&lup=4&maj=4&min=4&sub=4&scores=Atom%20Alignment,ECFP4,Daylight%27', function(data){
    console.log(data);
});
