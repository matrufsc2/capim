define("collections/BaseCollection", ["underscore", "chaplin", "bluebird"], function(_, Chaplin, Promise) {
	"use strict";
	var BaseCollection = Chaplin.Collection.extend({
		"fetch": function(options, callback){
			// Do the request using OboeJS, which allow progressive loading of the collection.
			options = _.defaults(options || {}, {
				"cached": true,
				"url": _.result(this, "url"),
				"type": "GET",
				"headers": null,
				"body": null
			});
			var context = options.context || this;
			var collection = this;
			var oldSuccess = options.success;
			var oldError = options.error;
			return (new Promise(function(resolve, reject) {
				collection.beginSync();
				options.success = resolve;
				options.error = reject;
				Chaplin.Collection.prototype.fetch.call(collection, options);
			}))
			.bind(context)
			.nodeify(callback)
			.then(function(){
				collection.finishSync();
				if (_.isFunction(oldSuccess)) {
					oldSuccess.apply(context, _.toArray(arguments));
				}
			}, function(){
				collection.abortSync();
				if (_.isFunction(oldError)) {
					oldError.apply(context, _.toArray(arguments));
				}
			});
		}
	});
	_.extend(BaseCollection.prototype, Chaplin.SyncMachine);
	return BaseCollection;
});