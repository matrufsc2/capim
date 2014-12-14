define("views/SelectedTeamView", [
		"templates",
		"jquery",
		"underscore", 
		"fastdom",
		"views/BaseView"
		], function(templates, $, _, fastdom, BaseView){
	"use strict";
	return BaseView.extend({
		"template" : templates.selectedTeam,
		"tagName": "tr",
		"events": {
			"mouseover": "focusTeam",
			"mouseout": "unfocusTeam",
			"click #selectedTeam": "updateSelectedTeam"
		},
		"initialize": function(options) {
			_.extend(this, _.pick(options, ["discipline", "selectedDisciplines"]));
			BaseView.prototype.initialize.apply(this, [options]);
		},
		"focusTeam": function(){
			if(this.discipline.team === this.model) {
				this.discipline.hoveredTeam = null;
				return;
			}
			this.discipline.hoveredTeam = this.model;
			this.selectedDisciplines.trigger("change:combination");
		},
		"unfocusTeam": function(){
			this.discipline.hoveredTeam = null;
			this.selectedDisciplines.trigger("change:combination");
		},
		"updateSelectedTeam": function(){
			this.model.set({
				"_selected": this.$("#selectedTeam").is(":checked")
			});
			this.selectedDisciplines.updateCombinations();
			this.selectedDisciplines.trigger("change:combination");
			this.render();
		},
		"getTemplateData": function(){
			return {
				"team": this.model
			};
		},
		"render": function(){
			BaseView.prototype.render.apply(this, []);
			fastdom.write(function(){
				var el = this.$("td");
				if(this.model.startGrouping){
					el.css("border-top", "4px #000000 solid");
				} else {
					el.css("border-top", "");
				}
				el.css({
					"background-color": this.discipline.get("_color"),
					"opacity": this.model.get("_selected") ? 1 : 0.5
				});

			}, this);
		},
		"dispose": function(){
			var view = this;
			this.$el.animate({
				"opacity": 0
			}, 400, function(){
				BaseView.prototype.dispose.apply(view, []);
			});
		}
	});
});