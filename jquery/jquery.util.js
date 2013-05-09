
// Name: createXMLDocument
// Input: String
// Output: XML Document
jQuery.createXMLDocument = function(string) {
	var browserName = navigator.appName;
	var doc;
	if (browserName == 'Microsoft Internet Explorer') {
		doc = new ActiveXObject('Msxml2.DOMDocument.3.0');//'Microsoft.XMLDOM'
		doc.async = 'false'
		doc.loadXML(string);
	} else {
		doc = (new DOMParser()).parseFromString(string, 'text/xml');
	}
	return doc;
}


// Name: createXMLDocument
// Input: String
// Output: XML Document
jQuery.findAttrInTagWAttr = function(doc, tagName, targetAttrName, attrName, attrValue) {
	// find the first occurence of the tag to improve performance
	var pos = doc.indexOf("<" + tagName);
	if (pos >= 0) {
		doc = doc.substr(pos, doc.length - pos);
	} else {
		doc = "";
	}
	
	var targetAttrValue = null;
	if (attrName && attrValue) {
		var regex = "<" + tagName + "\\s*[^>]*" + attrName + "\\s*=\\s*(['\"])" + attrValue + "\\1[^>]*>";
	} else {
		var regex = "<" + tagName + "\\s*[^>]*>";
	}
	var tag = doc.match(new RegExp(regex, "i")); // /<link\s+[^>]*rel\s*=\s*['"]shortcut icon['"][^>]*>/i);
	if (tag && tag.length > 0) {
		tag = tag[0]; // .match(new RegExp("href\\s*=\\s*(['\"])([^>]*)\\1", "i"))
		regex = "href\\s*=\\s*(['\"])([^'\"]*)\\1";
		targetAttrValue = tag.match(new RegExp(regex, "i"));
		if (targetAttrValue && targetAttrValue.length && targetAttrValue.length > 1) {
			targetAttrValue = targetAttrValue[2];
		} else {
			targetAttrValue = null;
		}
	}
	
	return targetAttrValue;
}

// Name: getAbsoluteLinkURL
// Function: get the absolute URL of a link according to its path and the context.
// link: the url in either absolute or relative path of the link.
// baseUrl: the url for current directory or the href attribute value of <base> tag in this page.
jQuery.getAbsoluteLinkURL = function(link, baseUrl) {
	// remove extra space characters at the begining and the end of the two parameters.
	link = link.replace(/^\s+/, "").replace(/\s+$/, "");
	
	if (link.match("^(\\w+://)?[^/\\.]+\\.[^/]+/")) {
		// link is a absolute URL
		return link;
	}
	
	// remove extra space characters at the begining and the end of the url and anything after the last / in the base url
	baseUrl = baseUrl.replace(/^\s+/, "").replace(/\s+$/, "");
	basePath = baseUrl.replace(new RegExp("[^/]*$"), "");
	
	// add / to the end of basePath it does not end with /
	basePath = basePath.replace(new RegExp("([^/])$"), "$1/");
		
	if (link.match("^/")) {
		// link starts with "/"											
		host = basePath.match("^(\\w+://)?[^/]+")[0];
		linkUrl = host + link;
	} else if (link.match("^./")) {
		// link starts with "./"
		// remove all occurrences of "./" and then concatenate it with the basePath.
		linkUrl = basePath + link.replace(new RegExp("./", "g"), "");
	} else if (link.match("^../")) {
		// link starts with "../"
		// add one more / before the / for the root directory in the path, 
		// e.g. "http://tomcat.office.zearon.com/wn/sdfdsf/df.jsp" will be changed into "http://tomcat.office.zearon.com//wn/sdfdsf/df.jsp".
		// this change will stop further removal of [^/]+/$ if the current directory is already the root.
		basePath = basePath.replace(new RegExp("(^(\\w+://)?[^/]+/)"), "$1/");
		
		// find occurrences of "../"
		parentDepth = link.match(new RegExp("../", "g")).length;
		for (var index = 0; index < parentDepth; ++ index) {
			// move basePath up the directory hierahchy
			basePath = basePath.replace(new RegExp("[^/]+/$"), "");
		}
		
		// remove the extra / before the / for the root directory in the path.
		basePath = basePath.replace(new RegExp("(^(\\w+://)?[^/]+)/"), "$1");
		
		linkUrl = basePath + link.replace(new RegExp("../", "g"), "");
	} else {
		// link starts with a sub directory of current dir.
		linkUrl = basePath + link;
	}
	
	return linkUrl;
}