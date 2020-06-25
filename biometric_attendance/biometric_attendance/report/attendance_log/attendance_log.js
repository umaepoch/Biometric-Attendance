frappe.query_reports["Attendance Log"] = {
	"filters": [
		{
		  "fieldname": "from_date",
		  "fieldtype": "Date",
		  "label": "From Date",
		  "default": get_today()
		},
		{
		  "fieldname": "to_date",
		  "fieldtype": "Date",
		  "label": "To Date",
		  "default": get_today()
		},
		{
		  "fieldname": "user",
		  "fieldtype": "Link",
		  "label": "User",
		  "options": "Biometric Users",
		  "reqd": 1,
		  "on_change": function() {
			var user = frappe.query_report.get_filter_value("user");
			console.log("user ----------"+user)
			if (user) {
				frappe.db.get_value("Biometric Users", user, "user_name", function(value) {
					console.log("---------------------"+value["user_name"])
					frappe.query_report.set_filter_value("user_name",value["user_name"]);
				});
			}
		  }
		},
		{
		  "fieldname": "user_name",
		  "fieldtype": "Data",
		  "label": "User Name",
		  "read_only": 1
		}
	]
}
