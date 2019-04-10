# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Auguria (<http://www.auguria.net>).
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
	"name": "Bibind website theme",
	"version": "1.0",
	"author": "Bibind",
	"website": "http://www.entre-polypes.com",
	"summary": "Bibind",
	"sequence": 0,
	"certificate": "",
	"license": "",
	"depends": [
			"website_blog",
			"website",
			"web",
			"base",
	],
	"category": "Generic Modules/Bibind",
	"complexity": "easy",
	"description": """
(English) Auguria 1234
====================================
Theme Bibind website.

(Français) Bibind 1234
====================================
Theme Bibind website.
	""",
	"qweb": [
	],
	"demo": [
	],
	"images": [
	],
	"data": [
		"security/security.xml",
		"security/ir.model.access.csv",
		"menu.xml",
		"views/partner.xml",
		"views/themes.xml",
		"views/website_templates.xml",
		"views/website_blog.xml",
	],
	"auto_install": False,
	"installable": True,
	"application": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: