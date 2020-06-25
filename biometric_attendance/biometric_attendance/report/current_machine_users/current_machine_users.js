// Copyright (c) 2016, Akshay Mehta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Current Machine Users"] = {
	"filters": [
		{
		"fieldname":"machine",
		"fieldtype":"Link",
		"options":"Biometric Machine",
		"Label":"Machine"
		}
	]
}
