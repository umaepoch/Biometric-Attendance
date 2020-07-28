// Copyright (c) 2019, Akshay Mehta and contributors
// For license information, please see license.txt

frappe.ui.form.on('Biometric Attendance', {
	refresh: function(frm) {
		console.log("ref working latField:"+frm.doc.latitude+"  lonField: "+frm.doc.longitude);
		frm.fields_dict.map_view.map.setView([frm.doc.latitude, frm.doc.longitude], 13);
		console.log(" lat val from map"+frm.fields_dict.map_view.map.getCenter()['lat']);
		console.log(" lng val from map"+frm.fields_dict.map_view.map.getCenter()['lng']);
	}
});

