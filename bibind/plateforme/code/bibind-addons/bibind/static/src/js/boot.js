/*---------------------------------------------------------
 * odoo Web Boostrap Code
 *---------------------------------------------------------*/

/**
 * @name odoo
 * @namespace odoo
 */
(function() {
    // copy everything in the odoo namespace to odoo.web
    odoo.web = _.clone(odoo);

    var inited = false;

    _.extend(odoo, {
        // Per session namespace
        // odoo.<module> will map to
        // odoo.instances.sessionname.<module> using a closure
        instances: {instance0: odoo},
        // links to the global odoo
        _odoo: odoo,
        // this unique id will be replaced by hostname_databasename by
        // odoo.web.Session on the first connection
        _session_id: "instance0",
        _modules: odoo._modules || ['web'],
        web_mobile: {},
        /**
         * odoo instance constructor
         *
         * @param {Array|String} modules list of modules to initialize
         */
        init: function(modules) {
            if (modules === undefined) {
                modules = odoo._modules;
            }
            modules = _.without(modules, "web");
            if (inited)
                throw new Error("odoo was already inited");
            inited = true;
            for(var i=0; i < modules.length; i++) {
                var fct = odoo[modules[i]];
                if (typeof(fct) === "function") {
                    odoo[modules[i]] = {};
                    for (var k in fct) {
                        odoo[modules[i]][k] = fct[k];
                    }
                    fct(odoo, odoo[modules[i]]);
                }
            }
            odoo._modules = ['web'].concat(modules);
            return odoo;
        }
    });
})();

