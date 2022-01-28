
odoo.bibind = function(instance, local) {
	console.log('rrrxxxrr');
	
	var _t = instance.web._t,
    _lt = instance.web._lt;
var QWeb = instance.web.qweb;
	
	
	instance.web.UserMenu.include({
	    template: "UserMenu",
	    
	    start: function() {
	    	 return this._super()
	    },
	    do_update: function () {
	    	 return this._super()
	    },
	    on_menu_help: function() {
	        window.open('http://dev.bibind.com/page/aboutus', '_blank');
	    },
	    
	    on_menu_settings: function() {
	        var self = this;
	        if (!this.getParent().has_uncommitted_changes()) {
	            self.rpc("/web/action/load", { action_id: "base.action_res_users_my" }).done(function(result) {
	                result.res_id = instance.session.uid;
	                self.getParent().action_manager.do_action(result);
	            });
	        }
	    },
	    on_menu_account: function() {
	    	 return this._super()
	    },
	    on_menu_about: function() {
	    	 return this._super()
	    },
	});
	
	
	
	
	
	
	
	
	 instance.web.ListView.include({
	
	        load_list: function(data) {
	        	  this._super(data);
	        	
	        	if (this.$buttons) {
	                this.$buttons.find('.oe_new_service_button').click(this.proxy('do_new_service_button')) ;
	            }
	        },
	        do_new_service_button: function () {
	            //implement your clic logic here  
	        	this.do_action({
	                name: _t("Creer un Service"),
	                type: "ir.actions.act_window",
	                res_model: "services.builder",
	                view_mode: 'form',
	                view_type: 'form',
	                views: [[false, 'form']],
	                target: 'new',
	                context: {}
	            });
	        }
	    });
	
	
	
	
    
    
    /**
    The progressbar field expect a float from 0 to 100.
*/
    
    instance.web.form.widgets.add('ProgressBarWrite', 'instance.bibind.FieldProgressBarWrite');
    
    
	instance.bibind.FieldProgressBarWrite = instance.web.form.AbstractField.extend({
	    template: 'FieldProgressBarWrite',
	    render_value: function() {
	        $('#id_write_field_progressbar').progressbar({
	            value: this.get('value') || 0,
	            
	        });
	        var formatted_value = instance.web.format_value(this.get('value') || 0, { type : 'float' });
	        this.$('span').html(formatted_value + '%');
	    }
	
	
	});
	
    
    
    
    instance.web.form.widgets.add('percentage', 'instance.bibind.PercentageWidget');
    instance.bibind.PercentageWidget = instance.web.form.FieldFloat.extend({

        list_of_per: {
            'percent' :  ['%', 100],
            'permil': ['&#8240;', 1000]
        },

        options : {
            'sign': 'percent'
        },

        display_name: _lt('PercentageWidget'),
        template: "PercentageWidget",
        render_value: function() {
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                var _value = parseFloat(this.get('value'));
                if (isNaN(_value)) {
                    this.$el.find(".percentage_filed").text('');
                }
                else{
                    this.$el.find(".percentage_filed").text((_value*100).toFixed(2) + '%');
                }
            }
        }
    });

    // list view
    instance.web.list.columns.add('field.percentage', 'instance.web.list.Percentage');
    instance.web.list.Percentage = instance.web.list.Column.extend({
        /**
         * Return a percentage format value
         *
         * @private
         */
        _format: function (row_data, options) {
            var _value = parseFloat(row_data[this.id].value);
            if (isNaN(_value)) {
                return null;
            }
            return (_value*100).toFixed(2) + '%';
        }
    });
    
    
    
    
    
    
    
    
    
    local.HomePage = instance.Widget.extend({
        start: function() {
        	var products = new local.ProductsWidget(
                    this, ["cpu", "mouse", "keyboard", "graphic card", "screen"], "#00FF00");
                products.appendTo(this.$el);
        },
    });
    
    
    local.ProductsWidget = instance.Widget.extend({
        template: "ProductsWidget",
        init: function(parent, products, color) {
            this._super(parent);
            this.products = products;
            this.color = color;
        },
    });

    
    

    local.csFieldSelection = instance.web.form.AbstractField.extend(instance.web.form.ReinitializeFieldMixin, {
        template: 'FieldSelection',
        events: {
            'change select': 'store_dom_value',
        },
        init: function(field_manager, node) {
            var self = this;
            console.log('init');
           
            
            
            this._super(field_manager, node);
          
            
            this.set("value", false);
            this.set("values", []);
            console.log('set value es init');
            this.records_orderer = new instance.web.DropMisordered();
            this.field_manager.on("view_content_has_changed", this, function() {
                var domain = new odoo.web.CompoundDomain(this.build_domain()).eval();
                if (! _.isEqual(domain, this.get("domain"))) {
                    this.set("domain", domain);
                }
            });
        },
        initialize_field: function() {
            instance.web.form.ReinitializeFieldMixin.initialize_field.call(this);
            this.on("change:domain", this, this.query_values);
            this.set("domain", new odoo.web.CompoundDomain(this.build_domain()).eval());
            this.on("change:values", this, this.render_value);
            console.log('initialize_field');
        },
        query_values: function() {
            var self = this;
            var def;
            console.log(this.field.type);
            if (this.field.type === "many2one") {
            	console.log('ffffmany');
                var model = new odoo.Model(odoo.session, this.field.relation);
                def = model.call("name_search", ['', this.get("domain")], {"context": this.build_context()});
            } else {
            	//var model = new odoo.Model(odoo.session, this.field);
                //def = model.call("name_search", ['', this.get("domain")], {"context": this.build_context()});
            
               console.log(' query values domain ffff');
               var d=this.get("domain")
           	var c=this.build_context()
           	console.log('query value d :'+d);
               console.log('objet field :');
               console.log($.parseJSON(JSON.stringify(this.field)));
              
            	var f=this.field.selection
               	console.log('field value d :'+f);

               
            	var values = _.reject(this.field.selection, function (v) { return v[0] === false && v[1] === ''; });
                def = $.when(values);
                console.log('def et :'+ self.get("values"));
                console.log($.parseJSON(JSON.stringify(this.records_orderer.add(def))));
            }
            if (! _.isEqual(values, self.get("values"))) {
            	console.log('ggggggrecord');
            	console.log(values);
               // self.set("values", values);
            }
            
            
            this.records_orderer.add(def).then(function(values) {
                if (! _.isEqual(values, self.get("values"))) {
                	console.log('record');
                	console.log(values);
                    self.set("values", values);
                }
            });
        },
        initialize_content: function() {
            // Flag indicating whether we're in an event chain containing a change
            // event on the select, in order to know what to do on keyup[RETURN]:
            // * If the user presses [RETURN] as part of changing the value of a
            //   selection, we should just let the value change and not let the
            //   event broadcast further (e.g. to validating the current state of
            //   the form in editable list view, which would lead to saving the
            //   current row or switching to the next one)
            // * If the user presses [RETURN] with a select closed (side-effect:
            //   also if the user opened the select and pressed [RETURN] without
            //   changing the selected value), takes the action as validating the
            //   row
            var ischanging = false;
            var $select = this.$el.find('select')
                .change(function () { ischanging = true; })
                .click(function () { ischanging = false; })
                .keyup(function (e) {
                    if (e.which !== 13 || !ischanging) { return; }
                    e.stopPropagation();
                    ischanging = false;
                });
            this.setupFocus($select);
        },
        commit_value: function () {
        	console.log('fcommitfff');
            this.store_dom_value();
            return this._super();
        },
        store_dom_value: function () {
        	console.log('storeffff');
        	var d=this.get("domain")
        	var c=this.build_context()
        	console.log('store d :'+d);
            console.log('store c :'+c);
            if (!this.get('effective_readonly') && this.$('select').length) {
                var val = JSON.parse(this.$('select').val());
                console.log(val);
                this.internal_set_value(val);
            }
        },
        set_value: function(value_) {
        	
        	
        	console.log('ffff set value');
            value_ = value_ === null ? false : value_;
            value_ = value_ instanceof Array ? value_[0] : value_;
            this._super(value_);
        },
        render_value: function() {
            var values = this.get("values");
            var d=this.get("domain")
        	var c=this.build_context()
        	console.log('render value d :'+d);
            console.log('render value c :'+c);
            console.log(values);
            console.log('render value');
            values =  [[false, this.node.attrs.placeholder || '']].concat(values);
            var found = _.find(values, function(el) { return el[0] === this.get("value"); }, this);
            if (! found) {
                found = [this.get("value"), _t('Unknown')];
                values = [found].concat(values);
            }
            if (! this.get("effective_readonly")) {
                this.$().html(QWeb.render("FieldSelectionSelect", {widget: this, values: values}));
                this.$("select").val(JSON.stringify(found[0]));
            } else {
                this.$el.text(found[1]);
            }
        },
        focus: function() {
            var input = this.$('select:first')[0];
            return input ? input.focus() : false;
        },
        set_dimensions: function (height, width) {
            this._super(height, width);
            this.$('select').css({
                height: height,
                width: width
            });
        }
    });

    instance.web.form.widgets.add('apiselection', 'instance.bibind.csFieldSelection');
    
    instance.web.client_actions.add('bibind.homepage', 'instance.bibind.HomePage');
    
    
}


