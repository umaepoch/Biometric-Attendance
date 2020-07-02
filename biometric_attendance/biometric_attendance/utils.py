import frappe
import time

@frappe.whitelist()
def get_biometric_user_name(user):
	return frappe.db.get_value("Biometric Users", { "name": user }, "user_name")

@frappe.whitelist()
def check_connection(machine_name=None):
	if not machine_name:
		return

	#from zk import ZK
	from biometric_attendance.biometric_attendance.zk import ZK

	machine_doc = frappe.get_doc("Biometric Machine", machine_name)

	conn = None

	success = False

	try:
		zk = ZK(machine_doc.ip_domain_address, machine_doc.port)
		conn = zk.connect()

		if conn:
			success = True

	except Exception as e:
		frappe.throw(e)

	finally:
		if conn:
			conn.disconnect()

	return success


@frappe.whitelist()
def import_attendance(machine_name=None):
	if not machine_name:
		return

	#from zk import ZK
	from biometric_attendance.biometric_attendance.zk import ZK

	machine_doc = frappe.get_doc("Biometric Machine", machine_name)

	conn = None

	success = False

	try:
		zk = ZK(machine_doc.ip_domain_address, machine_doc.port)
		conn = zk.connect()

		conn.read_sizes()
		i = 0

		attendance = conn.get_attendance()
		for a in attendance:
			get_list = frappe.get_list("Biometric Attendance" , filters={"timestamp":a.timestamp, "user_id": a.user_id}, fields=["name"])
			if len(get_list) == 0:
				attendance_doc = frappe.new_doc("Biometric Attendance")
				attendance_doc.uid = a.uid
				attendance_doc.user_id = a.user_id
				attendance_doc.timestamp = a.timestamp
				attendance_doc.punch = a.punch
				attendance_doc.status = a.status
				i = i + 1
				frappe.publish_realtime('import_biometric_attendance', dict(
							progress=i,
							total=conn.records
						), user=frappe.session.user)
				attendance_doc.save()
				attendance_doc.submit()
		success = True

	except Exception as e:
		frappe.throw(e)
	finally:
		if conn:
			conn.disconnect()

	return success

@frappe.whitelist()
def clear_machine_attendance(machine_name=None):
	if not machine_name:
		return

	#from zk import ZK
	from biometric_attendance.biometric_attendance.zk import ZK

	conn = None

	machine_doc = frappe.get_doc("Biometric Machine", machine_name)

	success = False

	try:
		zk = ZK(machine_doc.ip_domain_address, machine_doc.port)

		conn = zk.connect()

		conn.clear_attendance()

		success = True

	except Exception as e:
		frappe.throw(e)
	finally:
		if conn:
			conn.disconnect()

	return success

@frappe.whitelist()
def sync_users(machine_name=None):
	if not machine_name:
		return

	#from zk import ZK
	from biometric_attendance.biometric_attendance.zk import ZK

	conn = None

	machine_doc = frappe.get_doc("Biometric Machine", machine_name)

	success = False

	try:
		zk = ZK(machine_doc.ip_domain_address, machine_doc.port)

		conn = zk.connect()

		conn.read_sizes()

		if conn.records == 0:
			machine_users = conn.get_users()
			machine_user_ids = []
			system_user_ids = []
			for m in machine_users:
				machine_user_ids.append(m.user_id)

			for u in machine_doc.users:
				user_id = unicode(int(u.user[2:]))
				system_user_ids.append(user_id)

			for u in machine_doc.users:
				user_id = unicode(int(u.user[2:]))
				if user_id not in machine_user_ids:
					conn.set_user(user_id=user_id, name=u.user_name)

			for m in machine_users:
				if m.user_id not in system_user_ids:
					conn.delete_user(user_id=m.user_id)

			success = True

	except Exception as e:
		frappe.throw(e)
	finally:
		if conn:
			if conn.records > 0:
				frappe.msgprint("Attendance Records Exists")
			conn.disconnect()

	return success

@frappe.whitelist()
def delete_duplicate_rows_from_attendance():
	query = """
			delete t1 
			from 	`tabBiometric Attendance` t1 
				inner join 
				`tabBiometric Attendance` t2 
			where 
				t1.name < t2.name 
				and (t1.user_id = t2.user_id and t1.timestamp = t2.timestamp)
		"""

	frappe.db.sql(query)
	return True
