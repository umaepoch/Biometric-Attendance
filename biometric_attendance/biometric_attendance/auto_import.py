import frappe
import datetime
from frappe.utils import cint,  get_time, split_emails
from datetime import datetime, timedelta
machine_names = None
import datetime
from datetime import date
def get_time_difference_in_minutes(timeA, timeB):
	dateTimeA = datetime.datetime.combine(datetime.date.today(), timeA)
	dateTimeB = datetime.datetime.combine(datetime.date.today(), timeB)
	return (dateTimeA-dateTimeB).total_seconds() / 60

def put_machine_name_and_time():
	global machine_names
	machine_names = []
	
	machines = frappe.get_all("Biometric Machine")

	#created appending msg in created file called output.out
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	#f.write("machine name -------"+str(machines)+'\n')
	
	for m_name in machines:
		machine_doc = frappe.get_doc("Biometric Machine", m_name.name)
		#f.write("import_at -------"+str(machine_doc.import_at)+'\n')
		machine_names.append({
					'name': m_name.name,
					'import_at': machine_doc.import_at,
					'last_import_on': machine_doc.last_import_on,
					'import_enabled': machine_doc.auto_import_enabled,
					'retries': 0
				})
	f.close()
	return machine_names


def check_time_and_get_machine(machine_name):
	now_time = datetime.datetime.now().time()
	today_date = datetime.date.today()

	for m_name in machine_names:
		minute_diff = get_time_difference_in_minutes(get_time(now_time), get_time(m_name["import_at"]))
		if machine_name == m_name["name"]:
			if (cint(m_name["import_enabled"]) and m_name["last_import_on"] != today_date \
				and abs(minute_diff) <=50 and m_name["retries"] <= 3):
				return frappe.get_doc("Biometric Machine", m_name["name"])

	return None

def was_last_retry(machine):
	for m_name in machine_names:
		if m_name["name"] == machine.name:
			m_name["retries"] += 1
			if m_name["retries"] > 3:
				return True
			return False


@frappe.whitelist()
def auto_import(manual_import=0, machine_name=None):
	
	if not machine_names:
		put_machine_name_and_time()

	if not machine_name:
		for m_name in machine_names:
			auto_import_for_machine(machine_name=m_name["name"], manual_import=manual_import)
			user_doc(machine_name=m_name["name"], manual_import=manual_import)
			attendance_doc(machine_name=m_name["name"], manual_import=manual_import)
	else:
		auto_import_for_machine(machine_name=machine_name, manual_import=manual_import)
		user_doc(machine_name=machine_name, manual_import=manual_import)
		attendance_doc(machine_name=machine_name, manual_import=manual_import)

def auto_import_for_machine(machine_name, manual_import=0):
	if not machine_name:
		return

	if cint(manual_import):
		do_auto_import(machine=frappe.get_doc("Biometric Machine", machine_name), manual_import=1)
		
		
	else:
		do_auto_import(machine=check_time_and_get_machine(machine_name), manual_import=0)

def do_auto_import(machine, manual_import=0):
	from utils import import_attendance, clear_machine_attendance
	
	if not machine:
		return

	try:
		import_attendance(machine.name)
		
		if cint(machine.clear_after_import):
			clear_machine_attendance(machine.name)
		machine.last_import_on = datetime.date.today()
		machine.save()
		if not cint(manual_import):
			send_email(success=True, machine=machine)
	except Exception as e:
		if not cint(manual_import):
			if was_last_retry(machine):
				send_email(success=False, machine=machine, error_status=e)
		else:
			frappe.throw(e)

def send_email(success, machine, error_status=None):
	if not cint(machine.send_notification):
		return

	if success:
		subject = "Attendance Import Successful - {0}".format(machine.name)
		message ="""<h3>Attendance Imported Successfully</h3><p>Hi there, this is just to inform you
		that your attendance have been successfully imported.</p>"""
	else:
		subject = "[Warning] Attendance Import Failed - {0}".format(machine.name)
		message ="""<h3>Attendance Import has Failed</h3><p>Oops, your automated attendance Import has Failed</p>
		<p>Error message: <br>
		<pre><code>%s</code></pre>
		</p>
		<p>Please contact your system manager for more information.</p>
		""" % (error_status)

	recipients = split_emails(machine.notification_mail_address)
	frappe.sendmail(recipients=recipients, subject=subject, message=message)

def attendance_doc(machine_name, manual_import):
	if not machine_name:
		return None
	from zk import ZK

	machine_doc = frappe.get_doc("Biometric Machine", machine_name)

	conn = None

	success = False
	today = date.today()
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	zk = ZK(machine_doc.ip_domain_address, machine_doc.port)
	single_doc = frappe.get_single("Biometric Settings")
	conn = zk.connect()
	#f.write("conn -------"+str(conn)+'\n')
	
	if conn:
		attendance = conn.get_attendance()
		#f.write("attendance----------------"+str(attendance)+"\n")
		users = conn .get_users()
		create_attendance(attendance, users,machine_name,conn.records)

def create_attendance(attendance, users, machine_name,records = None):
	i = 0
	single_doc = frappe.get_single("Biometric Settings")
	
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	for a in attendance:
		time_date = a.timestamp.date()
		attendance_details = frappe.db.sql(""" select * from `tabBiometric Attendance` where user_id = %s and timestamp =%s and date= %s order by timestamp desc""",(a.user_id,a.timestamp,time_date), as_dict=1 )
		user_name = ""
		#f.write("attendance_details-----------------"+str(attendance_details)+"\n")
		for u in users:
			if u.user_id == a.user_id:
				user_name = u.name
		shift_type = ""
		if len(attendance_details) == 0:
			attendance_Record = get_attendace(a.user_id , a.timestamp)
		
			get_employee = frappe.get_value("Biometric Users", a.user_id, "employee")
			
			if get_employee:
				get_shift = frappe.get_list("Shift Assignment", filters = {"employee": get_employee}, fields=["shift_type"])
				if len(get_shift) != 0:
					shift_type = frappe.get_list("Shift Type", filters= {"name": get_shift[0]['shift_type']}, fields=["*"])
				lunch_start_time = ""
				shift_end_time = ""
				if len(shift_type) != 0:
					is_lunch_punch_mendatory = shift_type[0]['is_lunch_punch_mandatory']
					timestamp_date = a.timestamp.date()
					shift_end_time = shift_type[0]['end_time']
					shift_start_time = shift_type[0]['start_time']
					start_time = str(timestamp_date)+" "+str(shift_start_time)
					end_time = str(timestamp_date)+" "+str(shift_end_time)
					convert_end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
					convert_start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
					waiting_time = waiting_time_for_sign_in(single_doc.waiting_time_for_log_in,convert_start_time)
					if is_lunch_punch_mendatory == "Yes" or is_lunch_punch_mendatory== "Optional":
						lunch_start_time = shift_type[0]['lunch_start_time']
						lunch_end_time = shift_type[0]['lunch_end_time']
						lunch_time = str(timestamp_date)+" "+str(lunch_start_time)
						convert_lunch_time = datetime.datetime.strptime(lunch_time, '%Y-%m-%d %H:%M:%S')
						lunch_end_time = str(timestamp_date)+" "+str(lunch_end_time)
						con_lunch_end_time = datetime.datetime.strptime(lunch_end_time, '%Y-%m-%d %H:%M:%S')
						if convert_lunch_time <= a.timestamp:
							validate = frappe.get_list("Biometric Attendance", filters={"user_id": a.user_id , "date": timestamp_date, "punch": 2}, fields=["name",'timestamp'])
							if len(validate) == 0:
								punch = 0
								if a.punch > 0:
									punch = a.punch
								else:
									punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Lunch Out"}, fields=["punch_no"])
									punch = punch_status[0]['punch_no']
								attendance_doc = frappe.new_doc("Biometric Attendance")
								attendance_doc.uid = a.uid
								attendance_doc.user_id = a.user_id
								attendance_doc.timestamp = a.timestamp
								attendance_doc.punch = punch
								attendance_doc.status = a.status
								attendance_doc.user_name = user_name
								attendance_doc.date = timestamp_date
								attendance_doc.source = machine_name
								#attendance_doc.punch_status = "Before Lunch"
								i = i + 1
								frappe.publish_realtime('import_biometric_attendance', dict(
											progress=i,
											total=records
										), user=frappe.session.user)
								attendance_doc.save()
								attendance_doc.submit()
							else:
								validates = frappe.get_list("Biometric Attendance", filters={"user_id": a.user_id , "date": timestamp_date, "punch": 3}, fields=["name"])
								if len(validates) == 0 and con_lunch_end_time >= a.timestamp:
									
									punch = 0
									if a.punch > 0:
										punch = a.punch
									else:
										punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Lunch In"}, fields=["punch_no"])
										punch = punch_status[0]['punch_no']
									attendance_doc = frappe.new_doc("Biometric Attendance")
									attendance_doc.uid = a.uid
									attendance_doc.user_id = a.user_id
									attendance_doc.timestamp = a.timestamp
									attendance_doc.punch = punch
									attendance_doc.status = a.status
									attendance_doc.user_name = user_name
									attendance_doc.date = timestamp_date
									attendance_doc.source = machine_name
									#attendance_doc.punch_status = "After Lunch"
									i = i + 1
									frappe.publish_realtime('import_biometric_attendance', dict(
												progress=i,
												total=records
											), user=frappe.session.user)
									attendance_doc.save()
									attendance_doc.submit()
								
								elif convert_end_time <= a.timestamp:
									punch = 0
									if a.punch > 0:
										punch = a.punch
									else:
										punch_status = frappe.get_list("Punch Child", filters={"punch_type": "Check Out"}, fields=["punch_no"])
										punch = punch_status[0]['punch_no']
									attendance_doc = frappe.new_doc("Biometric Attendance")
									attendance_doc.uid = a.uid
									attendance_doc.user_id = a.user_id
									attendance_doc.timestamp = a.timestamp
									attendance_doc.punch = punch
									attendance_doc.status = a.status
									attendance_doc.user_name = user_name
									attendance_doc.date = timestamp_date
									attendance_doc.source = machine_name
									#attendance_doc.punch_status = "Log Out"
									i = i + 1
									frappe.publish_realtime('import_biometric_attendance', dict(
												progress=i,
												total=records
											), user=frappe.session.user)
									attendance_doc.save()
									attendance_doc.submit()
								else:
									punch = 0
									if a.punch > 0:
										punch = a.punch
									else:
										punch_status = frappe.get_list("Punch Child", filters={"punch_type": "Unknown Punch"}, fields=["punch_no"])
										punch = punch_status[0]['punch_no']
									attendance_doc = frappe.new_doc("Biometric Attendance")
									attendance_doc.uid = a.uid
									attendance_doc.user_id = a.user_id
									attendance_doc.timestamp = a.timestamp
									attendance_doc.punch = punch
									attendance_doc.status = a.status
									attendance_doc.user_name = user_name
									attendance_doc.date = timestamp_date
									attendance_doc.source = machine_name
									#attendance_doc.punch_status = ""
									i = i + 1
									frappe.publish_realtime('import_biometric_attendance', dict(
												progress=i,
												total=records
											), user=frappe.session.user)
									attendance_doc.save()
									attendance_doc.submit()
						elif waiting_time >= a.timestamp:
							punch = 0
							if a.punch > 0:
								punch = a.punch
							else:
								punch_status = frappe.get_list("Punch Child", filters={"punch_type": "Check In"}, fields=["punch_no"])
								
								punch = punch_status[0]['punch_no']
							attendance_doc = frappe.new_doc("Biometric Attendance")
							attendance_doc.uid = a.uid
							attendance_doc.user_id = a.user_id
							attendance_doc.timestamp = a.timestamp
							attendance_doc.punch = punch
							attendance_doc.status = a.status
							attendance_doc.user_name = user_name
							attendance_doc.date = timestamp_date
							attendance_doc.source = machine_name
							#attendance_doc.punch_status = "Log Out"
							i = i + 1
							frappe.publish_realtime('import_biometric_attendance', dict(
										progress=i,
										total=records
									), user=frappe.session.user)
							attendance_doc.save()
							attendance_doc.submit()
							
					else:
						if convert_end_time <=  a.timestamp:
							punch = 0
							if a.punch > 0:
								punch = a.punch
							else:
								punch_status = frappe.get_list("Punch Child", filters={"punch_type": "Check Out"}, fields=["punch_no"])
								punch = punch_status[0]['punch_no']
							attendance_doc = frappe.new_doc("Biometric Attendance")
							attendance_doc.uid = a.uid
							attendance_doc.user_id = a.user_id
							attendance_doc.timestamp = a.timestamp
							attendance_doc.punch = punch
							attendance_doc.status = a.status
							attendance_doc.user_name = user_name
							attendance_doc.date = timestamp_date
							attendance_doc.source = machine_name
							#attendance_doc.punch_status = "Log Out"
							i = i + 1
							frappe.publish_realtime('import_biometric_attendance', dict(
										progress=i,
										total=records
									), user=frappe.session.user)
							attendance_doc.save()
							attendance_doc.submit()
						elif waiting_time >= a.timestamp:
							punch = 0
							if a.punch > 0:
								punch = a.punch
							else:
								punch_status = frappe.get_list("Punch Child", filters={"punch_type": "Check In"}, fields=["punch_no"])
								punch = punch_status[0]['punch_no']
							attendance_doc = frappe.new_doc("Biometric Attendance")
							attendance_doc.uid = a.uid
							attendance_doc.user_id = a.user_id
							attendance_doc.timestamp = a.timestamp
							attendance_doc.punch = punch
							attendance_doc.status = a.status
							attendance_doc.user_name = user_name
							attendance_doc.date = timestamp_date
							attendance_doc.source = machine_name
							#attendance_doc.punch_status = "Log Out"
							i = i + 1
							frappe.publish_realtime('import_biometric_attendance', dict(
										progress=i,
										total=records
									), user=frappe.session.user)
							attendance_doc.save()
							attendance_doc.submit()
						else:
							
							punch_status = frappe.get_list("Punch Child", filters= {"punch_type": "Unknown Punch"}, fields=["punch_no"])
							punch = punch_status[0]['punch_no']
							
							attendance_doc = frappe.new_doc("Biometric Attendance")
							attendance_doc.uid = a.uid
							attendance_doc.user_id = a.user_id
							attendance_doc.timestamp = a.timestamp
							attendance_doc.punch = punch
							attendance_doc.status = a.status
							attendance_doc.user_name = user_name
							attendance_doc.date = timestamp_date
							attendance_doc.source = machine_name
							#attendance_doc.punch_status = ""
							i = i + 1
							frappe.publish_realtime('import_biometric_attendance', dict(
										progress=i,
										total=records
									), user=frappe.session.user)
							attendance_doc.save()
							attendance_doc.submit()
				else:
					punch_status = frappe.get_list("Punch Child", filters={"punch_type": "Unknown Punch"}, fields=["punch_no"])
					
					attendance_doc = frappe.new_doc("Biometric Attendance")
					attendance_doc.uid = a.uid
					attendance_doc.user_id = a.user_id
					attendance_doc.timestamp = a.timestamp
					attendance_doc.punch = punch_status[0]['punch_no']
					attendance_doc.status = a.status
					attendance_doc.user_name = user_name
					attendance_doc.date = timestamp_date
					attendance_doc.source = machine_name
					#attendance_doc.punch_status = ""
					i = i + 1
					frappe.publish_realtime('import_biometric_attendance', dict(
								progress=i,
								total=records
							), user=frappe.session.user)
					attendance_doc.save()
					attendance_doc.submit()
							
			else:
				punch = 0
				if a.punch:
					punch = a.punch
				timestamp_date = a.timestamp.date()
				attendance_doc = frappe.new_doc("Biometric Attendance")
				attendance_doc.uid = a.uid
				attendance_doc.user_id = a.user_id
				attendance_doc.timestamp = a.timestamp
				attendance_doc.punch = punch
				attendance_doc.status = a.status
				attendance_doc.user_name = user_name
				attendance_doc.date = timestamp_date
				attendance_doc.source = machine_name
				#attendance_doc.punch_status = ""
				i = i + 1
				frappe.publish_realtime('import_biometric_attendance', dict(
							progress=i,
							total=records
						), user=frappe.session.user)
				attendance_doc.save()
				attendance_doc.submit()
			
								
	f.close()
def user_doc(machine_name, manual_import):
	if not machine_name:
		return None
	from zk import ZK

	machine_doc = frappe.get_doc("Biometric Machine", machine_name)
	now = datetime.datetime.now()
	conn = None
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	zk = ZK(machine_doc.ip_domain_address, machine_doc.port)
	conn = zk.connect()
	users = []
	if conn:
		machine_users = conn.get_users()
		#f.write("conn -------"+str(machine_users)+'\n')
		for u in machine_users:
			users.append(u.user_id)
		#user_details = frappe.db.sql("""select * from `tabBiometric Users`""", as_dict=1 )
		if machine_users:
			for user in machine_users:
				
				user_details = frappe.db.sql(""" select * from `tabBiometric Users` where name = %s""",(user.user_id), as_dict=1 )			
				
				if len(user_details) == 0:
					user_doc = frappe.new_doc("Biometric Users")
					user_doc.user_name = user.name
					user_doc.is_active = "Yes"
					user_doc.branch = machine_doc.branch
					user_doc.timestamp = now
					user_doc.user_id = user.user_id
					user_doc.save()
	f.close()

def get_attendace(user_id , timestamp):
	today = date.today()
	records = frappe.db.sql("""select * from `tabBiometric Attendance` where user_id = %s and date = %s and docstatus =1 """,(user_id , today), as_dict=1)

	return records
def waiting_time_for_sign_in(waiting_time_login,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	#today = date.today()
	#sing_in_without_penalty = grade_details[0]['sign_in_without_penalty']
	#start_time_with_today_date = str(today)+" "+str(start_time)
	#convert_start_time = datetime.datetime.strptime(start_time_with_today_date, '%Y-%m-%d %H:%M:%S')
	addition_of_time = ""
	if waiting_time_login != 0:
		if waiting_time_login < 60:
			
			addition_of_time = start_time + timedelta(minutes=waiting_time_login)  
			
		elif waiting_time_login >= 60 and waiting_time_login < 120:
				minute = waiting_time_login - 60
				addition_of_time = start_time + timedelta(hours = 1,minutes=minute) 
		elif waiting_time_login >= 120 and waiting_time_login < 180:
				minute = waiting_time_login - 120
				addition_of_time = start_time + timedelta(hours = 2,minutes=minute)
	else:
		addition_of_time = start_time_with_today_date
	return addition_of_time
