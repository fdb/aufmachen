// Retrieves a page, loads it, and returns the final HTML to the console.
// Note that only the content of the <body> element is returned.
var url = phantom.args[0];
var page = new WebPage();
page.settings = {}
page.settings.loadImages = false;
page.settings.loadPlugins = false;
page.settings.userAgent = 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)';
page.open(url);
page.onLoadFinished = function(status) {
  if (status !== 'success') {
    console.log('err' + 'no body');
  }
  else {
    var html = page.evaluate(function() {
      return document.body.innerHTML;
    });
    console.log('ok ' + html);
  }
  phantom.exit();
};
