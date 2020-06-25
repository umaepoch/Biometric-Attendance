// Copyright (c) 2019, Akshay Mehta and contributors
// For license information, please see license.txt

frappe.ui.form.on("Enrolled Users", "user", function(frm, dt, dn) {
	var grid_row = cur_frm.open_grid_row();
	var user = null;
	var current_doc = null;

	if (!grid_row) {
		current_doc = frappe.get_doc(dt, dn);
		user = current_doc.user;
	} else {
		user = grid_row.grid_form.fields_dict.user.get_value();
	}

	if(user) {
		frappe.db.get_value("Biometric Users", user, "user_name", function(r) {
					if (grid_row) {
						grid_row.grid_form.fields_dict.user_name.set_value(r.user_name);
					} else {
						current_doc.user_name = r.user_name;
					}
					cur_frm.refresh_field('users');
		});
	}
});

frappe.ui.form.on("Biometric Machine", "refresh", function(frm) {
		if (!frm.doc.__islocal && frappe.user.has_role("System Manager", "HR Manager")) {
			frm.add_custom_button("Import Attendance", function() {
				frappe.call({
					method: "biometric_attendance.biometric_attendance.utils.import_attendance",
					args: { "machine_name": frm.doc.name },
					callback: function(r) {
						if (r.message) {
							frappe.msgprint("Success");
						}
					}
				});
			});
			frm.add_custom_button("Clear Machine Attendance", function() {
				frappe.call({
					method: "biometric_attendance.biometric_attendance.utils.clear_machine_attendance",
					args: { "machine_name": frm.doc.name },
					callback: function(r) {
						if (r.message) {
							frappe.msgprint("Success");
						}
					}
				});
			});
			frm.add_custom_button("Sync Users", function() {
				frappe.call({
					method: "biometric_attendance.biometric_attendance.utils.sync_users",
					args: { "machine_name": frm.doc.name },
					callback: function(r) {
						if (r.message) {
							frappe.msgprint("Success");
						}
					}
				});
			});
		}
});

frappe.ui.form.on("Biometric Machine", "refresh", function (frm) {
	frappe.realtime.on("import_biometric_attendance", function(data) {
		frappe.show_progress("Importing Attendance", data.progress, data.total);
		if (data.progress >= (data.total-1)) {
			frappe.hide_progress("import_biometric_attendance");
		}
	});
});


frappe.ui.form.on("Biometric Machine", "manual_import", function(frm) {
	if (!frappe.user.has_role("System Manager", "HR Manager")) {
		frappe.msgprint("Not Permitted");
		return;
	}
	frappe.call({
		method: "biometric_attendance.biometric_attendance.auto_import.auto_import",
		args: { "manual_import": 1, "machine_name": frm.doc.name },
		callback: function(r) {
			if (!r.exc) {
				frappe.msgprint("Success");
			}
		}
	});
});

frappe.ui.form.on("Biometric Machine", "check_connection", function(frm) {
	if (!frappe.user.has_role("System Manager", "HR Manager")) {
		frappe.msgprint("Not Permitted");
		return;
	}
	frappe.call({
		method: "biometric_attendance.biometric_attendance.utils.check_connection",
		args: { "machine_name": frm.doc.name },
		callback: function(r) {
			if (r.message) {
				frappe.msgprint("Success");
			}
		}
	});
});
