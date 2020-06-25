frappe.listview_settings['Biometric Machine'] = {
    onload: function(me) {
                me.page.add_menu_item(__("Delete Duplicate Attendance"), function() {
                        frappe.call({
                                method: "biometric_attendance.biometric_attendance.utils.delete_duplicate_rows_from_attendance",
                                callback: function(r) {
                                        if (!r.exc) {
                                                frappe.msgprint("Success");
                                        }
                                }
                        });
                });
    }
}

