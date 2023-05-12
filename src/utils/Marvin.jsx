import React from "react";
import PropTypes from "prop-types";


const Marvin = (props) => {
  
    const[marvinSketcherInstance, setMarvinSketcherInstance] = React.useState(null);
    const[Marvin, setMarvin] = React.useState(null);
    React.useEffect(() => {
        validateProps(props);
        
        window.MarvinJSUtil.getPackage("sketch").then(function (marvinNameSpace) {
			marvinNameSpace.onReady(function () {
				setMarvin(marvinNameSpace);
                console.log("MarvinJS is ready");
                marvinNameSpace.Sketch.license("https://marvinjs-demo.chemaxon.com/license/grant");
			});
		}, function () {
			alert("Cannot retrieve marvin instance from iframe");
		});
    }, []);


    React.useEffect(() => { 
        if (marvinSketcherInstance) {
            marvinSketcherInstance.importStructure(props.smiles, "smiles");
        }
    }, [props.smiles, marvinSketcherInstance]);
    
        return (
           	<div
                className="border rounded"
            >
                <iframe 
                    src="http://localhost:3000/Marvinjs/editor.html" 
                    id="sketch" 
                    class="sketcher-frame" 
                    data-toolbars="standard"
                    style={{width: props.width, height: props.height}}>
                </iframe>
            </div>

        );

};

const validateProps = (props) => {
    PropTypes.checkPropTypes(propTypes, props, 'prop', 'Marvin');
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

export default Marvin;

