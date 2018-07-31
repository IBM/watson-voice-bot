module.exports = {
	"env": {
	    "node": true,
	    "browser": true,
	    "jquery": true
  	},
    "extends": [	    
	    "eslint:recommended",
	    "google",
	    "plugin:node/recommended",
	    "prettier"
  	],
  	"plugins": [
  		"prettier",
  		"node"
  	],
  	"rules": {
	    "no-console": 0,
	    "no-process-exit": 0,	    	   
	    "prettier/prettier": ["error", {"singleQuote": true, "printWidth": 160}],
	    "prefer-const": "error",
	    "prefer-rest-params": "off",
	    "require-jsdoc": "off",
	    "valid-jsdoc": "off",
	    "camelcase": 2,
  }
};