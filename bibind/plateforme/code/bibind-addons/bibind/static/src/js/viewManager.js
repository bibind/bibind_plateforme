
(function() {

	var instance = odoo;
	
	var QWeb = instance.web.qweb,
	    _t = instance.web._t;
	

	
	instance.web.SearchView.include(/** @lends instance.web.SearchView# */{
	    template: "mdc-SearchView",
	   
	    

	});

	
	
instance.web.ActionManager.include({
	   
	});
	
instance.web.ViewManagerAction.include({
    template:"mdc-ViewManagerAction",
    
   
   
  
});

instance.web.form.FieldChar.include({
    template:"mdc-FieldChar",
    
   
   
  
});

instance.web.form.WidgetButton.include({
	 template:"mdc-WidgetButton",
})

instance.web.ViewManager.include({
    template: "mdc-ViewManager",

    /**
     * Sets up the current viewmanager's search view.
     *
     * @param {Number|false} view_id the view to use or false for a default one
     * @returns {jQuery.Deferred} search view startup deferred
     */
    setup_search_view: function(view_id, search_defaults) {
        var self = this;
        if (this.searchview) {
            this.searchview.destroy();
        }

        var options = {
            hidden: this.flags.search_view === false,
            disable_custom_filters: this.flags.search_disable_custom_filters,
        };
        this.searchview = new instance.web.SearchView(this, this.dataset, view_id, search_defaults, options);

        this.searchview.on('search_data', self, this.do_searchview_search);
        return this.searchview.appendTo($("#top_search_input"),
                                      $("#container_drawer_mdc"));
    },
    
    /**
     * Called when one of the view want to execute an action
     */
   
});




})()