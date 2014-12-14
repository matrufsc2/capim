define("controllers/BaseController", ["chaplin", "views/SiteView", "views/HeaderView", "views/FooterView"], function(Chaplin, SiteView, HeaderView, FooterView) {
  "use strict";
  return Chaplin.Controller.extend({
    beforeAction: function(params, route, options) {
      this.reuse("site", SiteView);
      this.reuse("header", {
        "compose": function(){
          return new HeaderView(route)
        },
        "check": function(){
          return true;
        }
      });
      this.reuse("footer", FooterView);
    }
  });
});