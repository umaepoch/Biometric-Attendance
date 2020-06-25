frappe.query_reports['Average Entry Exit Time'] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": get_today()
		},
		{
			"fieldname":"to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": get_today()
		},
		{
			"fieldname":"machine",
			"label": "Machine",
			"fieldtype": "Link",
			"default": "%%",
			"options": "Biometric Machine"
		}
	]
}
