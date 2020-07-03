// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Work"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"reqd": 1
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"reqd":1
		},
		{
			"fieldname":"reports_to",
			"label": __("Report To"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd": 1
		},
		{
			"fieldname":"date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		}
	]
}
