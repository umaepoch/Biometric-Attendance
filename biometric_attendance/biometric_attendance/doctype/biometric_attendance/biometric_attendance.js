// Copyright (c) 2019, Akshay Mehta and contributors
// For license information, please see license.txt

frappe.ui.form.on('Biometric Attendance', {
	refresh: function(frm) {
		//get_proper_dat_time()
		//console.log("refreshed");
		if(cur_frm.doc.status != 0){
			//console.log(" condition passed refreshed");


		set_user_full_name()
		cur_frm.set_value("timestamp", frappe.datetime.now_datetime());
		cur_frm.set_value("date", frappe.datetime.nowdate());
		cur_frm.set_value("source", "ERPNext Web");
		cur_frm.set_value("is_permitted_location", "Not Applicable");


		var test_array = set_punch_status_options()
		frm.set_df_property('punch_status', 'options', test_array);
		frm.refresh_field('punch_status');

		var emp_id = get_emp_id(frappe.session.user)
		cur_frm.set_value("employee_id", emp_id);


		//console.log("ref working latField:"+frm.doc.latitude+"  lonField: "+frm.doc.longitude);
		frm.fields_dict.map_view.map.setView([frm.doc.latitude, frm.doc.longitude], 13);
		frm.fields_dict.map_view_e.map.setView([frm.doc.latitude, frm.doc.longitude], 13);
		//console.log(" lat val from map"+frm.fields_dict.map_view.map.getCenter()['lat']);
		//console.log(" lng val from map"+frm.fields_dict.map_view.map.getCenter()['lng']);

		//web interface attendace

		//cur_frm.set_value("timestamp", frappe.datetime.now_datetime());
	}
	}
});

frappe.ui.form.on('Biometric Attendance', {
	punch_status: function(frm) {
		var data = set_punch_status_code(cur_frm.doc.punch_status)
		cur_frm.set_value("punch", data);
	}
});


function set_user_full_name() {
    var poList = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "User",
            filters: {
                name: ["=", frappe.session.user]
            },
            fieldname: ["full_name"]
        },
        async: false,
        callback: function(r) {
            console.log("full_name" + r.message.full_name);
						cur_frm.set_value("user_name", r.message.full_name);
        }
    });
    //frappe.validated = false;
    return poList;
}

function set_punch_status_options( ) {
	var temp_arr =[]
	//console.log("  Enterd set_punch_status_options" );
	frappe.call({
        method: "biometric_attendance.biometric_attendance.doctype.biometric_attendance.biometric_attendance.get_punch_status_list",
        async: false,
        callback: function(r) {
					if (r.message) {
					//	console.log("from set_punch_status_options"+JSON.stringify(r.message));
						 for (var i = 0; i < r.message.length; i++) {
								temp_arr.push(r.message[i])
						 }
					} else {
					//	console.log("failed to open custom api file ");
					}
				}  //end of call back
    }); // end of frappe call
		return temp_arr
} //  end of frappe_db_talk_check


function set_punch_status_code(punch_status ) {
	var punch_status_code ;
//	console.log("  Enterd set_punch_status_code" );
	frappe.call({
        method: "biometric_attendance.biometric_attendance.doctype.biometric_attendance.biometric_attendance.get_punch_status_code",
				args:{
					"punch_status":punch_status
				},
				async: false,
        callback: function(r) {
						//console.log("from set_punch_status_code"+r.message);
						punch_status_code = r.message;
				}  //end of call back
    }); // end of frappe call
		return punch_status_code
} //  end of frappe_db_talk_check


function get_emp_id(user_id ) {
	var emp_id_temp ;
//	console.log("  Enterd set_punch_status_code" );
	frappe.call({
        method: "biometric_attendance.biometric_attendance.doctype.biometric_attendance.biometric_attendance.get_employee_id",
				args:{
					"user_id":user_id
				},
				async: false,
        callback: function(r) {
						//console.log("from set_punch_status_code"+r.message);
						if(r.message){
							emp_id_temp = r.message;
						}
				}  //end of call back
    }); // end of frappe call
		return emp_id_temp
} //  end of frappe_db_talk_check

