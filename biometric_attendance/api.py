from __future__ import unicode_literals
import frappe
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import get_party_account_currency
from frappe.desk.notifications import clear_doctype_notifications
from datetime import datetime
from datetime import date
import sys
import os
import operator
import frappe
import json
import time
import math
import base64
from datetime import datetime, timedelta
import datetime
from biometric_attendance.zk import ZK
from frappe.cache_manager import clear_user_cache,clear_global_cache
from frappe.sessions import Session, clear_sessions

@frappe.whitelist()
def login_feed(login_manager):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	now = datetime.datetime.now()
	today = date.today()
	#f.write("today-------"+str(today)+'\n')
	#f.write("now-------"+str(now)+'\n')
	#today = str(today)+" 09:00:00"
	get_employee_id = frappe.get_list("Employee", filters={"user_id":login_manager.user}, fields=['user_id', 'name'])
	
	#f.write("get_employee_id-------"+str(get_employee_id)+'\n')

	if get_employee_id:
		
		for emp in get_employee_id:
			name = emp['name']
			shift = frappe.get_list("Shift Assignment", filters = {"employee": name}, fields=["shift_type"])
			get_shift_time = frappe.get_list("Shift Type", filters = {"name": shift[0]['shift_type']}, fields=["start_time", "end_time"])
			start_time = get_shift_time[0]['start_time']
			today = str(today)+" "+str(start_time)
			user_details = frappe.get_list("Biometric Users", filters={"employee":name}, fields=['name','user_name','branch'])
			attendance_details = frappe.db.sql("""select * from `tabBiometric Attendance` where user_id = %s and timestamp >= %s and timestamp <= %s""",(user_details[0]['name'],today,now), as_dict=1 )
			
			#f.write("sid-------"+str(frappe.session)+'\n')
			if attendance_details:
				pass
			else:
				clear_sessions(login_manager.user)
				raise frappe.AuthenticationError(_('There is not Attendance'))

def check_attendance_leave_before_time():
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	current_datetime = datetime.datetime.now()
	today = date.today()
	attendance = get_attendance(today)
	all_attendance = get_attendance_all(today)
	if all_attendance:
		for atn in all_attendance:
			
			user_id = atn.user_id
			date_d = atn.date
			employee_id = get_employee(user_id)
			shift = get_shift(employee_id)
			if shift:
				end_time = shift[0]['end_time']
				shift_end_time = str(date_d)+" "+str(end_time)
				convert_shift_end_time = datetime.datetime.strptime(shift_end_time, '%Y-%m-%d %H:%M:%S')
				waiting_time = single_doc.waiting_time_for_log_out
				waiting_datetime = waiting_time_prepared(waiting_time,convert_shift_end_time)
				if current_datetime >= waiting_datetime:
					logout_punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Check Out"}, fields=["punch_no"])
					unknown_punch = frappe.get_list("Punch Child",filters= {"punch_type": "Unknown Punch"}, fields=["punch_no"])
					check_log_out = get_logout_punch(user_id,today,logout_punch_status)
					if len(check_log_out) == 0:
						if shift[0]['is_lunch_punch_mandatory'] == 'Yes' or shift[0]['is_lunch_punch_mandatory'] == 'Optional':
							lunchout_punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Lunch Out"}, fields=["punch_no"])
							check_next_status = get_next_status(user_id,today,lunchout_punch_status)
							if len(check_next_status) != 0:
								lunchin_punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Lunch In"}, fields=["punch_no"])
								check_after_lunch = get_after_lunch(check_next_status[0]['user_id'], today,lunchin_punch_status)
								if len(check_after_lunch) != 0:
									check_null_punch = get_null_punch_after(check_after_lunch,unknown_punch)
									if len(check_null_punch) != 0:
										frappe.db.set_value("Biometric Attendance", check_null_punch[0].name, "punch", 1)
									else:
										'''
										uid = atn.uid
										uid = int(uid)+1
										attendance_doc = frappe.new_doc("Biometric Attendance")
										attendance_doc.uid = uid
										attendance_doc.user_id = atn.user_id
										attendance_doc.timestamp = current_datetime
										attendance_doc.punch = atn.punch
										attendance_doc.status = atn.status
										attendance_doc.user_name = atn.user_name
										attendance_doc.date = today
										attendance_doc.source = atn.machine_name
										attendance_doc.punch = 1
										attendance_doc.save()
										attendance_doc.submit()
										'''
										pass
								else:
							
									frappe.db.set_value("Biometric Attendance", check_next_status[0]['name'], "punch", 1)
							else:
								'''
								uid = atn.uid
								uid = int(uid)+1
								attendance_doc = frappe.new_doc("Biometric Attendance")
								attendance_doc.uid = uid
								attendance_doc.user_id = atn.user_id
								attendance_doc.timestamp = current_datetime
								attendance_doc.punch = atn.punch
								attendance_doc.status = atn.status
								attendance_doc.user_name = atn.user_name
								attendance_doc.date = today
								attendance_doc.source = atn.machine_name
								attendance_doc.punch = 1
								attendance_doc.save()
								attendance_doc.submit()
								'''
								pass
					
						else:
							check_null_punch = get_null_punch(user_id,atn.timestamp,unknown_punch)
							if len(check_null_punch) != 0:
								frappe.db.set_value("Biometric Attendance", check_null_punch[0].name, "punch", 1)
							else:
								'''
								uid = atn.uid
								uid = int(uid)+1
								attendance_doc = frappe.new_doc("Biometric Attendance")
								attendance_doc.uid = uid
								attendance_doc.user_id = atn.user_id
								attendance_doc.timestamp = current_datetime
								attendance_doc.punch = atn.punch
								attendance_doc.status = atn.status
								attendance_doc.user_name = atn.user_name
								attendance_doc.date = today
								attendance_doc.source = atn.machine_name
								attendance_doc.punch = 1
								attendance_doc.save()
								attendance_doc.submit()
								'''
								pass
					else:
						pass
		'''	
				#f.write("shift timing -----------------"+str(shift)+'\n')
		if attendance:
			for atn in attendance:
				user_name = atn
			
				#f.write("punch status-----------------"+str(atn.punch)+"\n")
			
				if atn.punch is "" or atn.punch is None:
					frappe.db.set_value("Biometric Attendance", atn.name, "punch", 1)
		'''
def get_attendance(today):
	attendance = frappe.db.sql("""select * from `tabBiometric Attendance` t1 inner join(select Max(timestamp) as mxdate, user_id from `tabBiometric Attendance` group by user_id)t2 on t1.user_id = t2.user_id and t1.timestamp = t2.mxdate and t1.date = %s""",today,as_dict=1)
	return attendance
	
def get_attendance_all(today):
	all_atendance = frappe.get_list("Biometric Attendance", filters={"date":today, "punch":0}, fields=["*"])
	return all_atendance
def get_employee(user_id):
	get_employee = frappe.get_list("Biometric Users", filters={"name":user_id}, fields=["employee"])
	return get_employee
def get_shift(employee_id):
	get_shift_time = ""
	if employee_id:
		shift = frappe.get_list("Shift Assignment", filters = {"employee": employee_id[0]['employee']}, fields=["shift_type"])
		if shift:
			get_shift_time = frappe.get_list("Shift Type", filters = {"name": shift[0]['shift_type']}, fields=["*"])
	return get_shift_time

def get_next_status(user_id,today,lunchout_punch_status):
	next_punch = frappe.get_list("Biometric Attendance", filters={"user_id":user_id, "date":today, "punch":lunchout_punch_status[0]['punch_no']}, fields=["*"])
	return next_punch

def get_after_lunch(user_id, today,lunchin_punch_status):
	next_punch = frappe.get_list("Biometric Attendance", filters={"user_id":user_id, "date":today, "punch":lunchin_punch_status[0]['punch_no']}, fields=["*"])
	return next_punch
def get_logout_punch(user_id,today,logout_punch_status):
	logout_punch = frappe.get_list("Biometric Attendance", filters={"user_id":user_id, "date":today, "punch":logout_punch_status[0]['punch_no']}, fields=["*"])
	return logout_punch
def waiting_time_prepared(waiting_time,convert_shift_end_time):
	addition_of_time = ""
	if waiting_time != 0:
		if waiting_time < 60:
			
			addition_of_time = convert_shift_end_time + timedelta(minutes=waiting_time)  
			
		elif waiting_time >= 60 and waiting_time < 120:
			minute = waiting_time - 60
			addition_of_time = convert_shift_end_time + timedelta(hours = 1,minutes=minute)

		elif waiting_time >= 120 and waiting_time < 180:
			minute = waiting_time - 120
			addition_of_time = convert_shift_end_time + timedelta(hours = 2,minutes=minute)
	else:
		addition_of_time = convert_shift_end_time
	return addition_of_time

def get_null_punch_after(check_after_lunch,unknown_punch):
	current_date = check_after_lunch[0]['timestamp'].date()
	null_punch = frappe.db.sql(""" select * from `tabBiometric Attendance` where user_id = %s and punch = %s and timestamp > %s and date = %s""", (check_after_lunch[0]['user_id'], check_after_lunch[0]['timestamp'],current_date,unknown_punch[0]['punch_no']), as_dict=1)
	return null_punch

def get_null_punch(user_id,timestamp,unknown_punch):
	current_date = timestamp.date()
	null_punch = frappe.db.sql(""" select * from `tabBiometric Attendance` where user_id = %s and punch = %s and timestamp > %s and date = %s""", (user_id, timestamp,current_date,unknown_punch[0]['punch_no']), as_dict=1)
	return null_punch
