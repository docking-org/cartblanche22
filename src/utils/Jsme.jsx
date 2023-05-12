import React from "react";
import PropTypes from "prop-types";
import initRDKit from '../utils/initRDKit';

const Jsme = (props) => {
 

    const[jsmeApplet, setJsmeApplet] = React.useState(null);
    React.useEffect(() => {
      
        //make this a global function so that it can be called from the script
        function jsmeOnLoad() {
            if(window.JSApplet){
            let Applet = new window.JSApplet.JSME("jsme_container", props.width, props.height, {
            
                "smiles": props.smiles
            });
            window.jsmeApplet = Applet;
            setJsmeApplet(Applet);
        }
        }
        window.jsmeOnLoad = jsmeOnLoad;

        const script = document.createElement('script');
        script.src = props.src;
        script.async = true;
        script.onload = jsmeOnLoad;
        document.body.appendChild(script);
    }, []);


    React.useEffect(() => { 
        
        if(jsmeApplet){
            jsmeApplet.setCallBack("AfterStructureModified", (function (event) {
                console.log(event)
                var smiles = event.src.smiles();
                
                if (props.onChange) {
                    props.onChange(smiles);
                }
            }));
            
            jsmeApplet.readGenericMolecularInput(props.smiles);
        }
        
       
    }, [props.smiles, jsmeApplet]);
    
    return (
        <div id="jsme_container"></div>

 );


};

const validateProps = (props) => {
    PropTypes.checkPropTypes(propTypes, props, 'prop', 'Jsme');
    return props;
};

const propTypes = {
  height: PropTypes.string.isRequired,
  width: PropTypes.string.isRequired,
  smiles: PropTypes.string,
  options: PropTypes.string,
  onChange: PropTypes.func,
  src: PropTypes.string
};

export default Jsme;

