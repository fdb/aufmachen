// Retrieves a page, loads it, and returns the final HTML to the console.
// Note that only the contents of the <body> element is returned.
var url = phantom.args[0];
var page = new WebPage();
page.open(url);
page.onLoadFinished = function(status) {
  var html = page.evaluate(function() {
    return document.body.innerHTML;
  });
  console.log(html);
  phantom.exit();
};