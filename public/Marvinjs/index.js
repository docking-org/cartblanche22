'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

function _interopDefault (ex) { return (ex && (typeof ex === 'object') && 'default' in ex) ? ex['default'] : ex; }

var React = _interopDefault(require('react'));
var PropTypes = _interopDefault(require('prop-types'));

function _classCallCheck(instance, Constructor) {
  if (!(instance instanceof Constructor)) {
    throw new TypeError("Cannot call a class as a function");
  }
}

function _defineProperties(target, props) {
  for (var i = 0; i < props.length; i++) {
    var descriptor = props[i];
    descriptor.enumerable = descriptor.enumerable || false;
    descriptor.configurable = true;
    if ("value" in descriptor) descriptor.writable = true;
    Object.defineProperty(target, descriptor.key, descriptor);
  }
}

function _createClass(Constructor, protoProps, staticProps) {
  if (protoProps) _defineProperties(Constructor.prototype, protoProps);
  if (staticProps) _defineProperties(Constructor, staticProps);
  return Constructor;
}

function _defineProperty(obj, key, value) {
  if (key in obj) {
    Object.defineProperty(obj, key, {
      value: value,
      enumerable: true,
      configurable: true,
      writable: true
    });
  } else {
    obj[key] = value;
  }

  return obj;
}

function _inherits(subClass, superClass) {
  if (typeof superClass !== "function" && superClass !== null) {
    throw new TypeError("Super expression must either be null or a function");
  }

  subClass.prototype = Object.create(superClass && superClass.prototype, {
    constructor: {
      value: subClass,
      writable: true,
      configurable: true
    }
  });
  if (superClass) _setPrototypeOf(subClass, superClass);
}

function _getPrototypeOf(o) {
  _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) {
    return o.__proto__ || Object.getPrototypeOf(o);
  };
  return _getPrototypeOf(o);
}

function _setPrototypeOf(o, p) {
  _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) {
    o.__proto__ = p;
    return o;
  };

  return _setPrototypeOf(o, p);
}

function _assertThisInitialized(self) {
  if (self === void 0) {
    throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  }

  return self;
}

function _possibleConstructorReturn(self, call) {
  if (call && (typeof call === "object" || typeof call === "function")) {
    return call;
  }

  return _assertThisInitialized(self);
}


function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}


var scripts= ['/js/marvinjslauncher.js','./js/lib/jquery-3.6.0.min.js','./js/lib/rainbow/rainbow-custom.min.js','./js/lib/promise-1.0.0.min.js']
var stylesheets = ['./css/doc.css','./js/lib/rainbow/github.css']
var marvinSketcherInstance;

function setup() {
  scripts.forEach(function (script) {
    var scriptTag = document.createElement('script');
    scriptTag.src = script;
    document.body.appendChild(scriptTag);
  }
  )
  stylesheets.forEach(function (stylesheet) {
    var linkTag = document.createElement('link');
    linkTag.rel = 'stylesheet';
    linkTag.href = stylesheet;
    document.head.appendChild(linkTag);
  }
  )

 
}

var Marvin =
/*#__PURE__*/
function (_React$PureComponent) {
  _inherits(Marvin, _React$PureComponent);

  function Marvin(props) {

    //below is the javascript version to load marvin
    //		$(document).ready(function handleDocumentReady (e) {
			// after editor in the sketch iframe is ready store its reference 
		// 	// and activate controls
		// 	MarvinJSUtil.getEditor("#sketch").then(function (sketcherInstance) {
		// 
    //marvinSketcherInstance = sketcherInstance;
		// 		initControls();
		// 	},function (error) {
		// 		alert("Cannot retrieve sketcher instance from iframe:"+error);
		// 	});
		// });

		// function initControls () {
		// 	// change layout
		// 	$("input[name='defaulttool-group']").change(function(e) {
		// 		var s = $(this).val();
		// 		updateDefaultTool(s);
		// 	});
		// }

		// function updateDefaultTool(tool) {
		// 	marvinSketcherInstance.setDisplaySettings({
		// 		"defaultTool": tool
		// 	});
		// }

    //we need to load the marvin sketcher here in a react way
    var _this;

    _classCallCheck(this, Marvin);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(Marvin).call(this, props));
    _defineProperty(_assertThisInitialized(_this), "handleLoad", function () {
      _this.MarvinJS = window.MarvinJSUtil.getEditor("#sketch");
      _this.MarvinJS.then(function (sketcherInstance) {
        _this.sketcherInstance = sketcherInstance;
        _this.sketcherInstance.on("molchange", _this.handleChange);
        _this.sketcherInstance.importStructure("mol", _this.props.value);
      }
      );

      


    });
    _defineProperty(_assertThisInitialized(_this), "handleChange", function (jsmeEvent) {
    
    });

    _this.myRef = React.createRef();
    _this.id = "marvin" + getRandomInt(1, 100000);
    return _this;
  }

  _createClass(Marvin, [{
    key: "componentDidMount",
    value: function componentDidMount() {
        setup();
    }
  }, {
    key: "componentWillUnmount",
    value: function componentWillUnmount() {
      
    }
  }, {
    key: "componentDidUpdate",
    value: function componentDidUpdate(prevProps) {
      
      
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement("div", {
        ref: this.myRef,
        id: this.id
      });
    }
  }]);

  return Marvin;
}(React.PureComponent);
Marvin.propTypes = {
  height: PropTypes.string.isRequired,
  width: PropTypes.string.isRequired,
  smiles: PropTypes.string,
  options: PropTypes.string,
  onChange: PropTypes.func,
  src: PropTypes.string
};

exports.Marvin = Marvin;
exports.setup = setup;
//# sourceMappingURL=index.js.map
