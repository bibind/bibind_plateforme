# -*- encoding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2010-2013 Auguria (<http://www.auguria.net>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
	"name": "Bibind Cloud Service",
	"version": "1.0",
	"author": "Bibind",
	"website": "http://www.entre-polypes.com",
	"summary": "Bibind Cloud services",
	"sequence": 0,
	"certificate": "",
	"license": "",
	"depends": [
			"web",
			"portal",
			"base",
			"product",
			"sale",
			"mail",
			
	],
	"category": "Generic Modules/Bibind",
	"complexity": "easy",
	"description": """
(English) Bibind Application
====================================
Application for continous intégration and delivary développement.

(Français) Bibind Application
====================================
Application pour l'intégration et la livraison continue.
Proposition SAAS, IAAS, PAAS
	""",
	"test": [
	],
	"js": [
		"static/src/js/cloudservice.js",
		"static/src/js/pourcentageWidget.js",
		"static/src/js/materials/material.js",
		"static/src/js/materials/ripples.js",
	],
	"css": [
		"static/src/css/cloudservice.css",
		"static/src/css/materials/bootstrap-material-design.css",
		"static/src/css/materials/ripples.min.css",
		"static/src/css/materials/index.css",
		"static/src/css/materials/styles.css",
	],
	"qweb": [
			"static/src/xml/cloudservice.xml",
	],
	"demo_xml": [
	],
	"images": [
	],
	"init_xml": [
		
	],
	"data": [
	    "menu.xml",
	    "security/security.xml",
        "security/ir.model.access.csv",
		"wizard/services_builder_view.xml",
		"views/webclient_templates.xml",
		"views/compute/cloudservice_base.xml",
		"views/container/container.xml",
		"views/cloud_launch_scripts.xml",
		"views/cloudservice_api_fournisseur.xml",
		"views/cloudservice_fournisseur.xml",
		"views/cloudservice.xml",
		"views/cloudservice_product.xml",
		"views/applications/applications.xml",
		"views/cloudservice_me.xml",
		"views/cloudservice_fournisseur.xml",
		"views/cloud_service_sequence.xml",
		"data/bibind_partner.xml",
		"views/services/services.xml",
		"views/services/delivery_continous/delivery_continous.xml",
		"views/depots/depots.xml",
	],
	"auto_install": False,
	"installable": True,
	"application": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: