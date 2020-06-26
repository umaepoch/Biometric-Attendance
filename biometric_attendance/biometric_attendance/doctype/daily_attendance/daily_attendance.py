# -*- coding: utf-8 -*-
# Copyright (c) 2020, Akshay Mehta and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import datetime
from datetime import date
from datetime import datetime
import datetime 
import calendar
import time
from datetime import timedelta  
from frappe.utils import time_diff_in_hours
#f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
class DailyAttendance(Document):
	pass

@frappe.whitelist()
def create_attedance():
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	today = date.today()
	single_doc = frappe.get_single("Biometric Settings")
	
	attendance = frappe.db.sql("""select * from `tabBiometric Attendance` where  date = %s and docstatus=1  order by user_id""",today ,as_dict =1)
	
	unified_attendance = get_unique_attendance(attendance)

	for atn in unified_attendance:
		attnadance_record = unified_attendance[atn]
		prepare_attendance = get_prepare_attendance(atn,attnadance_record)
	
	#employee_list = frappe.db.sql("""select * from `tabEmployee` emp , `Shift Assignment` s)	
	
#arrange the attendance for each user id 
def get_unique_attendance(attendance):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	data = {}
	
	for att in attendance:
		key = att.user_id
		if len(data) != 0:
			if key in data:
				data[key].append({"user_id":key ,"timestamp": att.timestamp, "user_name": att.user_name, "punch": att.punch , "punch":att.punch})
			else:
				data[key]=[{"user_id":key ,"timestamp": att.timestamp, "user_name": att.user_name, "punch": att.punch, "punch":att.punch}]
			
		else:
			data[key]=[{"user_id":key ,"timestamp": att.timestamp, "user_name": att.user_name,"punch": att.punch, "punch":att.punch}]
	return data

#preparethe attendance according rules 
def get_prepare_attendance(user_id, attnadance_record):
	
	today = date.today()
	current_datetime = datetime.datetime.now()
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	#f.write("attnadance_record-------------"+str(attnadance_record)+"\n")
	single_doc = frappe.get_single("Biometric Settings")
	validate_log_in = False
	validate_log_out = False
	get_employee = frappe.get_list("Biometric Users", filters={"name":user_id}, fields=["employee"])
	
	if len(get_employee) != 0:
		get_shift = frappe.get_list("Shift Assignment", filters = {"employee": get_employee[0]['employee']}, fields=["shift_type"])
		get_shift_time = ""
		start_time = ""
		end_time = ""
		grade_details = ""
		log_in_punch = False
		log_out_punch = False
		if get_shift:
			get_shift_time = frappe.get_list("Shift Type", filters = {"name": get_shift[0]['shift_type']}, fields=["start_time", "end_time"])
			start_time = get_shift_time[0]['start_time']
			
			end_time = get_shift_time[0]['end_time']
			
			grade = frappe.get_list("Employee", filters={"name":get_employee[0]['employee']}, fields = ['grade'])
			grade_details = frappe.get_list("Employee Grade", filters={"name":grade[0]['grade']}, fields = ["*"])

			start_shift = str(today)+" "+str(start_time)
			convert_shift_start_time = datetime.datetime.strptime(start_shift, '%Y-%m-%d %H:%M:%S')
			end_shift = str(today)+" "+str(end_time)
			convert_shift_end_time = datetime.datetime.strptime(end_shift, '%Y-%m-%d %H:%M:%S')
			waiting_time = single_doc.waiting_time_for_log_out
			waiting_datetime = waiting_time_prepared(waiting_time,convert_shift_end_time)
			penalty_status = ""
			half_day = False
			if current_datetime >= waiting_datetime:
				sing_in_time = sing_in_time_without_penalty(grade_details,start_time,today)
				sign_in_with_p = sing_in_time_with_penalty(grade_details,start_time,today)
				sign_out_without_p = sing_out_time_without_penalty(grade_details,end_time,today)
				sign_out_with_p = sing_out_time_with_penalty(grade_details,end_time,today)
				total_can_be_late_in_a_month = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
				can_be_late_in_month = grade_details[0]['can_be_late_in_month']
				can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
				login_time = ""
				logout_time = ""
				
				lunchout_punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Lunch Out"}, fields=["punch_no"])
				lunchin_punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Lunch In"}, fields=["punch_no"])
				login_punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Check In"}, fields=["punch_no"])
				logout_punch_status = frappe.get_list("Punch Child",filters= {"punch_type": "Check Out"}, fields=["punch_no"])
				unknow_punch = frappe.get_list("Punch Child",filters= {"punch_type": "Unknown Punch"}, fields=["punch_no"])
				for atn in attnadance_record:
					user_id = atn['user_id']
					if login_punch_status[0]['punch_no'] in [at['punch'] for at in attnadance_record]:
						if atn['punch'] == login_punch_status[0]['punch_no']:
							timestamp = atn['timestamp']
							timestamp_time = timestamp.strftime("%H:%M:%S")
							login_time = timestamp
							if sing_in_time < timestamp:
								login_time = timestamp

								if sign_in_with_p >= timestamp:
								
									time = timestamp.strftime("%M:%S")
								
									now = datetime.datetime.now()
									week_late = check_week_late(user_id,today,grade_details,start_time)
								
									if week_late['get_time_week'] == True:
										penalty_status = "Rule Number 1"
										validate_log_in = True
									elif  week_late['exceed_total_minute'] == True:
										penalty_status = "Rule Number 3"
										validate_log_in = True
								

									elif week_late['get_time_week'] == False and week_late['exceed_total_minute'] == False:
										month_late = check_month_late(user_id,today,grade_details,start_time)
										if month_late['total_no_month'] == True:
											penalty_status = "Rule Number 2"
											validate_log_in = True
										if  month_late['exceed_total_time'] == True:
											penalty_status = "Rule Number 3"
											validate_log_in = True
								elif sign_in_with_p < timestamp:
									month_late = check_month_late_for_total(user_id,today,grade_details,start_time)
									if month_late == True:
										penalty_status = "Rule Number 3"
										validate_log_in = True
							elif sing_in_time >= timestamp and timestamp > convert_shift_start_time:
								month_late = check_month_late_without_p(user_id,today,grade_details,start_time)
								if month_late == True:
									penalty_status = "Rule Number 3"
									validate_log_in = True
					else:
						if lunchout_punch_status[0]['punch_no'] in [d['punch'] for d in attnadance_record]:
							if lunchin_punch_status[0]['punch_no'] in [d['punch'] for d in attnadance_record]:
								log_in_punch = True
							else:
								
								timestamp = atn['timestamp']
								login_time = timestamp
								half_day = True	
								
						else:
							if logout_punch_status[0]['punch_no'] in [d['punch'] for d in attnadance_record]:
								log_in_punch = True
				for atn in attnadance_record:

					if logout_punch_status[0]['punch_no'] in [at['punch'] for at in attnadance_record]:
						if atn['punch'] == logout_punch_status[0]['punch_no']:
							user_id = atn['user_id']
							timestamp = atn['timestamp']
							#timestamp_time = timestamp.strftime("%H:%M:%S")
							#get_time = convert_time.strftime("%H:%M:%S")
							logout_time = timestamp
							if sign_out_without_p > timestamp:
								logout_time = timestamp

								if sign_out_with_p <= timestamp:
									week_late = check_week_late_log_out(user_id,today,grade_details,end_time)
									if week_late['get_time_week'] == True:
										penalty_status = "Rule Number 1"
										validate_log_out = True
									elif week_late['exceed_total_minute'] == True:
										penalty_status = "Rule Number 3"
										validate_log_out = True
									elif week_late['get_time_week'] == False and week_late['exceed_total_minute'] == False:
										month_late = check_month_late_log_out(user_id,today,grade_details,end_time)
									
										if month_late['total_no_month'] == True:
											penalty_status = "Rule Number 2"
											validate_log_out = True
										elif month_late['exceed_time'] == True:
											penalty_status = "Rule Number 3"
											validate_log_out = True
								elif sign_out_with_p > timestamp:
									month_late = check_month_late_log_out_for_total(user_id,today,grade_details,end_time)
									if month_late == True:
										penalty_status = "Rule Number 3"
										validate_log_out = True
							elif sign_out_without_p <= timestamp and timestamp < convert_shift_end_time:
								month_late = check_month_late_log_out_without_p(user_id,today,grade_details,end_time)
								if month_late == True:
									penalty_status = "Rule Number 3"
									validate_log_out = True
					else:
						if lunchout_punch_status[0]['punch_no'] in [at['punch'] for at in attnadance_record]:
							if lunchin_punch_status[0]['punch_no'] in [at['punch'] for at in attnadance_record]:
								log_out_punch = True
							else:
								timestamp = atn['timestamp']
								logout_time = timestamp
								half_day = True	
						
						else:
							
							log_out_punch = True
				
				if half_day == True:
					validat = frappe.get_list("Daily Attendance" , filters={"employee_id":get_employee[0]['employee'], "date":today}, fields=["name"])
					if len(validat) == 0:
						minutes_late_without_p = 0
						minutes_late_with_p = 0
						minutes_logout_with_p = 0
						minutes_logout_without_p = 0
						'''
						if logout_time:
							if sign_out_without_p < logout_time and logout_time < convert_shift_end_time :
								sub =    convert_shift_end_time - logout_time
								minutes_logout_without_p = sub.seconds/60
							elif sign_out_with_p <= logout_time and logout_time < sign_out_without_p:
								sub =    convert_shift_end_time - logout_time
								minutes_logout_with_p = sub.seconds/60
						'''
						if minutes_logout_with_p < 0:
							minutes_logout_with_p = 0

						if minutes_logout_without_p < 0:
							minutes_logout_without_p = 0

						doc = frappe.new_doc("Daily Attendance")
					
						doc.user_name = atn['user_name']
						doc.user_id = atn['user_id']
						doc.status = 'Half Day'
						doc.employee_id = get_employee[0]['employee']
						doc.date = today
						doc.late_punch_out_without_penalty = minutes_logout_without_p
						doc.late_punch_out_with_penalty = minutes_logout_with_p
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.punch_in_time = login_time
						doc.punch_out_time = logout_time
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.sign_in_without_penalty = grade_details[0]['sign_in_without_penalty']
						doc.sign_in_with_penalty = grade_details[0]['sign_in_with_penalty']
						doc.sign_out_with_penalty = grade_details[0]['sign_out_with_penalty']
						doc.sign_out_without_penalty = grade_details[0]['sign_out_without_penalty']
						#doc.can_be_late_in_month = grade_details[0]['can_be_late_in_month']
						#doc.can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
						#doc.total_no_of_minutes_can_be_late_in_a_month = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
						doc.reason_for_non_conformance = ""
						get_details = prepare_child_details(grade_details)
						for d in get_details:
							child_doc = doc.append('rules',{})
							child_doc.rule_number = d["rule_number"]
							child_doc.rule_description = d["rule_description"]
							child_doc.rule_value = d["rule_value"]
					
						doc.save()
						doc.submit()
				elif log_in_punch == True:
					validat = frappe.get_list("Daily Attendance" , filters={"employee_id":get_employee[0]['employee'], "date":today}, fields=["name"])
					if len(validat) == 0:
						minutes_late_without_p = 0
						minutes_late_with_p = 0
						minutes_logout_with_p = 0
						minutes_logout_without_p = 0
						if login_time:
							if sing_in_time >= login_time and login_time > convert_shift_start_time:
								sub =  login_time - convert_shift_start_time
								minutes_late_without_p = sub.seconds/60
							elif sign_in_with_p >= login_time and login_time > sing_in_time:
								sub =  login_time - convert_shift_start_time
								minutes_late_with_p = sub.seconds/60
						if logout_time:
							if sign_out_without_p < logout_time and logout_time < convert_shift_end_time :
								sub =    convert_shift_end_time - logout_time
								minutes_logout_without_p = sub.seconds/60
							elif sign_out_with_p <= logout_time and logout_time < sign_out_without_p:
								sub =    convert_shift_end_time - logout_time
								minutes_logout_with_p = sub.seconds/60
						if minutes_logout_with_p < 0:
							minutes_logout_with_p = 0

						if minutes_logout_without_p < 0:
							minutes_logout_without_p = 0

						if minutes_late_with_p < 0:
							minutes_late_with_p = 0

						if minutes_late_without_p < 0:
							minutes_late_without_p = 0

						doc = frappe.new_doc("Daily Attendance")
					
						doc.user_name = atn['user_name']
						doc.user_id = atn['user_id']
						doc.status = ''
						doc.employee_id = get_employee[0]['employee']
						doc.date = today
						doc.late_punch_out_without_penalty = minutes_logout_without_p
						doc.late_punch_out_with_penalty = minutes_logout_with_p
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.punch_in_time = login_time
						doc.punch_out_time = logout_time
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.sign_in_without_penalty = grade_details[0]['sign_in_without_penalty']
						doc.sign_in_with_penalty = grade_details[0]['sign_in_with_penalty']
						doc.sign_out_with_penalty = grade_details[0]['sign_out_with_penalty']
						doc.sign_out_without_penalty = grade_details[0]['sign_out_without_penalty']
						#doc.can_be_late_in_month = grade_details[0]['can_be_late_in_month']
						#doc.can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
						#doc.total_no_of_minutes_can_be_late_in_a_month = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
						doc.reason_for_non_conformance = "Missed Log in Punch"
						get_details = prepare_child_details(grade_details)
						for d in get_details:
							child_doc = doc.append('rules',{})
							child_doc.rule_number = d["rule_number"]
							child_doc.rule_description = d["rule_description"]
							child_doc.rule_value = d["rule_value"]
					
						doc.save()
				elif log_out_punch == True:
					validat = frappe.get_list("Daily Attendance" , filters={"employee_id":get_employee[0]['employee'], "date":today}, fields=["name"])
					if len(validat) == 0:
						minutes_late_without_p = 0
						minutes_late_with_p = 0
						minutes_logout_with_p = 0
						minutes_logout_without_p = 0
						if login_time:
							if sing_in_time >= login_time and login_time > convert_shift_start_time:
								sub =  login_time - convert_shift_start_time
								minutes_late_without_p = sub.seconds/60
							elif sign_in_with_p >= login_time and login_time > sing_in_time:
								sub =  login_time - convert_shift_start_time
								minutes_late_with_p = sub.seconds/60
						if logout_time:
							if sign_out_without_p < logout_time and logout_time < convert_shift_end_time :
								sub =    convert_shift_end_time - logout_time
								minutes_logout_without_p = sub.seconds/60
							elif sign_out_with_p <= logout_time and logout_time < sign_out_without_p:
								sub =    convert_shift_end_time - logout_time
								minutes_logout_with_p = sub.seconds/60
						if minutes_logout_with_p < 0:
							minutes_logout_with_p = 0

						if minutes_logout_without_p < 0:
							minutes_logout_without_p = 0

						if minutes_late_with_p < 0:
							minutes_late_with_p = 0

						if minutes_late_without_p < 0:
							minutes_late_without_p = 0

						doc = frappe.new_doc("Daily Attendance")
				
						doc.user_name = atn['user_name']
						doc.user_id = atn['user_id']
						doc.status = ''
						doc.employee_id = get_employee[0]['employee']
						doc.date = today
						doc.late_punch_out_without_penalty = minutes_logout_without_p
						doc.late_punch_out_with_penalty = minutes_logout_with_p
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.punch_in_time = login_time
						doc.punch_out_time = logout_time
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.sign_in_without_penalty = grade_details[0]['sign_in_without_penalty']
						doc.sign_in_with_penalty = grade_details[0]['sign_in_with_penalty']
						doc.sign_out_with_penalty = grade_details[0]['sign_out_with_penalty']
						doc.sign_out_without_penalty = grade_details[0]['sign_out_without_penalty']
						#doc.can_be_late_in_month = grade_details[0]['can_be_late_in_month']
						#doc.can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
						#doc.total_no_of_minutes_can_be_late_in_a_month = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
						doc.reason_for_non_conformance = "Missed Log out Punch"
						get_details = prepare_child_details(grade_details)
						for d in get_details:
							child_doc = doc.append('rules',{})
							child_doc.rule_number = d["rule_number"]
							child_doc.rule_description = d["rule_description"]
							child_doc.rule_value = d["rule_value"]
				
						doc.save()
				elif validate_log_out == False and validate_log_in == False:
					validat = frappe.get_list("Daily Attendance" , filters={"employee_id":get_employee[0]['employee'], "date":today}, fields=["name"])
					if len(validat) == 0:
						minutes_late_without_p = 0
						minutes_late_with_p = 0
						minutes_logout_with_p = 0
						minutes_logout_without_p = 0
						if sing_in_time >= login_time and login_time > convert_shift_start_time:
							sub =  login_time - convert_shift_start_time
							minutes_late_without_p = sub.seconds/60
						elif sign_in_with_p >= login_time and login_time > sing_in_time:
							sub =  login_time - convert_shift_start_time
							minutes_late_with_p = sub.seconds/60
						if sign_out_without_p < logout_time and logout_time < convert_shift_end_time :
							sub =    convert_shift_end_time - logout_time
							minutes_logout_without_p = sub.seconds/60
						elif sign_out_with_p <= logout_time and logout_time < sign_out_without_p:
							sub =    convert_shift_end_time - logout_time
							minutes_logout_with_p = sub.seconds/60
						if minutes_logout_with_p < 0:
							minutes_logout_with_p = 0

						if minutes_logout_without_p < 0:
							minutes_logout_without_p = 0

						if minutes_late_with_p < 0:
							minutes_late_with_p = 0

						if minutes_late_without_p < 0:
							minutes_late_without_p = 0

						doc = frappe.new_doc("Daily Attendance")
						
						doc.user_name = atn['user_name']
						doc.user_id = atn['user_id']
						doc.status = 'Present'
						doc.employee_id = get_employee[0]['employee']
						doc.date = today
						doc.late_punch_out_without_penalty = minutes_logout_without_p
						doc.late_punch_out_with_penalty = minutes_logout_with_p
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.punch_in_time = login_time
						doc.punch_out_time = logout_time
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.sign_in_without_penalty = grade_details[0]['sign_in_without_penalty']
						doc.sign_in_with_penalty = grade_details[0]['sign_in_with_penalty']
						doc.sign_out_with_penalty = grade_details[0]['sign_out_with_penalty']
						doc.sign_out_without_penalty = grade_details[0]['sign_out_without_penalty']
						#doc.can_be_late_in_month = grade_details[0]['can_be_late_in_month']
						#doc.can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
						#doc.total_no_of_minutes_can_be_late_in_a_month = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
						doc.reason_for_non_conformance = penalty_status
						get_details = prepare_child_details(grade_details)
						for d in get_details:
							child_doc = doc.append('rules',{})
							child_doc.rule_number = d["rule_number"]
							child_doc.rule_description = d["rule_description"]
							child_doc.rule_value = d["rule_value"]
						
						doc.save()
						doc.submit()
				else:
					validat = frappe.get_list("Daily Attendance" , filters={"employee_id":get_employee[0]['employee'], "date":today}, fields=["name"])
					if len(validat) == 0:
				
				
						minutes_late_without_p = 0
						minutes_late_with_p = 0
						minutes_logout_with_p = 0
						minutes_logout_without_p = 0

						if sing_in_time > login_time and login_time > convert_shift_start_time:
							sub =  login_time - convert_shift_start_time
							minutes_late_without_p = sub.seconds/60

						elif sign_in_with_p >= login_time and login_time > convert_shift_start_time:
							sub =  login_time - convert_shift_start_time
							minutes_late_with_p = sub.seconds/60
						if logout_time:
							if sign_out_without_p <= logout_time and logout_time < convert_shift_end_time:
								sub =  convert_shift_end_time - logout_time 
								minutes_logout_without_p = sub.seconds/60

							elif sign_out_with_p <= logout_time and   logout_time < sign_out_without_p:
								sub =   convert_shift_end_time - logout_time
								minutes_logout_with_p = sub.seconds/60

						if minutes_logout_with_p < 0:
							minutes_logout_with_p = 0

						if minutes_logout_without_p < 0:
							minutes_logout_without_p = 0

						if minutes_late_with_p < 0:
							minutes_late_with_p = 0

						if minutes_late_without_p < 0:
							minutes_late_without_p = 0

						doc = frappe.new_doc("Daily Attendance")
						doc.user_name = atn['user_name']
						doc.user_id = atn['user_id']
						doc.status = 'Half Day'
						doc.employee_id = get_employee[0]['employee']
						doc.date = today
						doc.punch_in_time = login_time
						doc.punch_out_time = logout_time
						doc.late_punch_out_without_penalty = minutes_logout_without_p
						doc.late_punch_out_with_penalty = minutes_logout_with_p
						doc.late_punch_in_without_penalty = minutes_late_without_p
						doc.late_punch_in_with_penalty = minutes_late_with_p
						doc.sign_in_without_penalty = grade_details[0]['sign_in_without_penalty']
						doc.sign_in_with_penalty = grade_details[0]['sign_in_with_penalty']
						doc.sign_out_with_penalty = grade_details[0]['sign_out_with_penalty']
						doc.sign_out_without_penalty = grade_details[0]['sign_out_without_penalty']
						#doc.can_be_late_in_month = grade_details[0]['can_be_late_in_month']
						#doc.can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
						#doc.total_no_of_minutes_can_be_late_in_a_month = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
						#f.write("penalty_status---------------"+str(penalty_status)+"\n")
						doc.reason_for_non_conformance = penalty_status
						get_details = prepare_child_details(grade_details)
						for d in get_details:
							child_doc = doc.append('rules',{})
							child_doc.rule_number = d["rule_number"]
							child_doc.rule_description = d["rule_description"]
							child_doc.rule_value = d["rule_value"]
						doc.save()
				
def prepare_child_details(grade_details):
	data = []
	datas = {"rule_number": "Rule Number 1" , "rule_description":"can be late sign in/early sign out in a week" , "rule_value": grade_details[0]['can_be_late_in_a_week']}
	data.append(datas)
	datas =  {"rule_number": "Rule Number 2" , "rule_description":"can be late sign in/early sign out in a month" , "rule_value": grade_details[0]['can_be_late_in_month']}
	data.append(datas)
	datas =  {"rule_number": "Rule Number 3" , "rule_description":"can be late sign in/early sign out total no of minutes in a month" , "rule_value": grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']}
	data.append(datas)
	return data
def check_week_late(user_id,today,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
	Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	i = 0
	minutes = 0
	count_true = 0
	get_time_week = False
	exceed_total_minute = False
	while i < datetime.datetime.today().weekday():
		j =1 + i
		Previous_Dates = datetime.datetime.today() - datetime.timedelta(days=j)
		Previous_Dates = Previous_Dates.date()
		start_datetime = str(Previous_Dates)+" "+str(start_time)
		convert_start_time = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
		previouse_attendance = get_previouse_attendance(user_id,Previous_Dates)
		get_time_ween_no = check_time(previouse_attendance,grade_details,start_time)
		
		if get_time_ween_no == True:
			count_true += 1
		
		else:		
			i += 1
		if previouse_attendance :
			timestamp = previouse_attendance[0]['timestamp']
			sub_time = timestamp - convert_start_time
			minutes_d = sub_time.seconds/60
			minutes += minutes_d
			
		
		if count_true > can_be_late_in_a_week :
			get_time_week = True
			break
		elif total_minutes > 0:
			
			if minutes > total_minutes:
				exceed_total_minute = True
				break
		
	return {"get_time_week":get_time_week,"exceed_total_minute":exceed_total_minute}

def check_week_late_log_out(user_id,today,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
	i = 0
	can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	count_true = 0
	minutes = 0
	get_time_week = False
	exceed_total_minute = False
	while i < datetime.datetime.today().weekday():
		j =1 + i
		Previous_Dates = datetime.datetime.today() - datetime.timedelta(days=j)
		Previous_Dates = Previous_Dates.date()
		previouse_attendance = get_previouse_attendance_log_out(user_id,Previous_Dates)
		get_time_ween_no = check_time_log_out(previouse_attendance,grade_details,end_time)
		end_datetime = str(Previous_Dates)+" "+str(end_time)
		convert_end_time = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
		
		if get_time_ween_no == True:
			count_true += 1
			timestamp = previouse_attendance[0]['timestamp']
			sub_time = convert_end_time - timestamp
			minutes_d = sub_time.seconds/60
			minutes += minutes_d
		else:		
			i += 1
		if count_true > can_be_late_in_a_week:
			get_time_week = True
			break
		if total_minutes > 0:
			if minutes > total_minutes:
				exceed_total_minute = True
				break
	return {"get_time_week":get_time_week,"exceed_total_minute":exceed_total_minute}
def check_time(previouse_attendance,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	flag = False
	total_time = 0
	if len(previouse_attendance) != 0:
		for pre_atn in previouse_attendance:
			timestamp = pre_atn.timestamp
			pre_date = pre_atn.date
			sign_in_with_p = sing_in_time_with_penalty(grade_details,start_time,pre_date)
			atn_month = pre_date.strftime("%B")
			sub_time = timestamp - sign_in_with_p
			if cur_month == atn_month:
				if sign_in_with_p < timestamp:
					#sub_time = timestamp - sign_in_with_p
					flag = True
					break
	return flag
def check_time_for_month(previouse_attendance,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	can_be_late_in_month = grade_details[0]['can_be_late_in_month']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	total_no_month = False
	i = 0
	total_time = 0
	minutes = 0
	exceed_total_time = False
	if len(previouse_attendance) != 0:
		for pre_atn in previouse_attendance:
			timestamp = pre_atn.timestamp
			pre_date = pre_atn.date
			sign_in_with_p = sing_in_time_with_penalty(grade_details,start_time,pre_date)
			start_datetime = str(pre_date)+" "+str(start_time)
			convert_start_time = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
			atn_month = pre_date.strftime("%B")
			if cur_month == atn_month:
				if sign_in_with_p < timestamp:
					sub_time = timestamp - convert_start_time
					minutes_d = sub_time.seconds/60
					minutes += minutes_d
					i += 1	
				if i > can_be_late_in_month:
					total_no_month = True
					break
				if total_minutes > 0:
					if minutes > total_minutes:
						exceed_total_time = True
						break
	return {"total_no_month":total_no_month, "exceed_total_time":exceed_total_time}
def check_time_for_month_total_minute(previouse_attendance,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	can_be_late_in_month = grade_details[0]['can_be_late_in_month']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	flag = False
	i = 0
	total_time = 0
	minutes = 0
	if len(previouse_attendance) != 0:
		for pre_atn in previouse_attendance:
			timestamp = pre_atn.timestamp
			pre_date = pre_atn.date
			sign_in_with_p = sing_in_time_with_penalty(grade_details,start_time,pre_date)
			start_datetime = str(pre_date)+" "+str(start_time)
			convert_start_time = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
			atn_month = pre_date.strftime("%B")
			if cur_month == atn_month:
				if sign_in_with_p < timestamp:
					sub_time = timestamp - convert_start_time
					minutes_d = sub_time.seconds/60
					minutes += minutes_d
					i += 1
				if total_minutes > 0:
					if minutes > total_minutes:
						flag = True
						break
	return flag

def check_time_for_month_without_p(month_attendance,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	can_be_late_in_month = grade_details[0]['can_be_late_in_month']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	if total_minutes > 0:
		flag = False
		i = 0
		total_time = 0
		minutes = 0
		if len(month_attendance) != 0:
			for pre_atn in month_attendance:
				timestamp = pre_atn.timestamp
				pre_date = pre_atn.date
				sign_in_with_p = sing_in_time_without_penalty(grade_details,start_time,pre_date)
				start_datetime = str(pre_date)+" "+str(start_time)
				convert_start_time = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
				atn_month = pre_date.strftime("%B")
				if cur_month == atn_month:
					if sign_in_with_p < timestamp:
						sub_time = timestamp - convert_start_time
						minutes_d = sub_time.seconds/60
						minutes += minutes_d
						i += 1
					if total_minutes > 0:
						if minutes > total_minutes:
							flag = True
							break
	return flag

def check_time_log_out(previouse_attendance,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	can_be_late_in_a_week = grade_details[0]['can_be_late_in_a_week']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	flag = False
	i = 0
	if len(previouse_attendance) != 0:
		for pre_atn in previouse_attendance:
			timestamp = pre_atn.timestamp
			pre_date = pre_atn.date
			sign_out_with_p = sing_out_time_with_penalty(grade_details,end_time,pre_date)
			sign_out_without_p = sing_out_time_without_penalty(grade_details,end_time,pre_date)
			atn_month = pre_date.strftime("%B")
			if cur_month == atn_month:
				if sign_out_with_p <= timestamp and timestamp < sign_out_without_p:
					flag = True
					break
	return flag		
def check_time_log_out_for_month(previouse_attendance,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	can_be_late_in_month = grade_details[0]['can_be_late_in_month']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	total_no_month = False
	exceed_time = False
	minutes = 0
	i = 0
	if len(previouse_attendance) != 0:
		for pre_atn in previouse_attendance:
			timestamp = pre_atn.timestamp
			pre_date = pre_atn.date
			sign_out_with_p = sing_out_time_with_penalty(grade_details,end_time,pre_date)
			sign_out_without_p = sing_out_time_without_penalty(grade_details,end_time,pre_date)
			end_datetime = str(pre_date)+" "+str(end_time)
			convert_end_time = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
			atn_month = pre_date.strftime("%B")
			if cur_month == atn_month:
				if sign_out_with_p <= timestamp and timestamp < sign_out_without_p:
					sub_time = convert_end_time - timestamp
					minutes_d = sub_time.seconds/60
					minutes += minutes_d
					i = i + 1
				if i > can_be_late_in_month:
					total_no_month = True
					break
				if total_minutes > 0:
					if minutes > total_minutes:
						exceed_time = True
						break
	return {"total_no_month":total_no_month, "exceed_time":exceed_time}
def check_time_log_out_for_month_for_total(month_attendance,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	can_be_late_in_month = grade_details[0]['can_be_late_in_month']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	flag = False
	i = 0
	minutes = 0
	if len(month_attendance) != 0:
		for pre_atn in month_attendance:
			timestamp = pre_atn.timestamp
			pre_date = pre_atn.date
			end_datetime = str(pre_date)+" "+str(end_time)
			convert_end_time = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
			sign_out_with_p = sing_out_time_with_penalty(grade_details,end_time,pre_date)
			atn_month = pre_date.strftime("%B")
			if cur_month == atn_month:
				if sign_out_with_p > timestamp:
					sub_time = convert_end_time - timestamp
					minutes_d = sub_time.seconds/60
					minutes += minutes_d
				if total_minutes > 0:	
					if minutes > total_minutes:
						flag = True
						break
				
	return flag
def check_time_log_out_for_month_without_p(previouse_attendance,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	single_doc = frappe.get_single("Biometric Settings")
	mydate = datetime.datetime.now()
	cur_month = mydate.strftime("%B")
	can_be_late_in_month = grade_details[0]['can_be_late_in_month']
	total_minutes = grade_details[0]['total_no_of_minutes_can_be_late_in_a_month']
	flag = False
	i = 0
	minutes = 0
	if len(previouse_attendance) != 0:
		for pre_atn in previouse_attendance:
			timestamp = pre_atn.timestamp
			pre_date = pre_atn.date
			sign_out_without_p = sing_out_time_without_penalty(grade_details,end_time,pre_date)
			atn_month = pre_date.strftime("%B")
			end_datetime = str(pre_date)+" "+str(end_time)
			convert_end_time = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
			if cur_month == atn_month:
				if sign_out_without_p <= timestamp and timestamp < convert_end_time:
					sub_time = convert_end_time - timestamp
					minutes_d = sub_time.seconds/60
					minutes += minutes_d
				if total_minutes > 0:
					if minutes > total_minutes:
						flag = True
						break
				
	return flag
def get_previouse_attendance(user_id,Previous_Dates):
	date = Previous_Dates.strftime("%Y-%m-%d")
	attendance = frappe.get_list("Biometric Attendance", filters={"user_id": user_id, "date":date , "punch":0}, fields=["*"])
	return attendance

def get_previouse_attendance_log_out(user_id,Previous_Dates):
	date = Previous_Dates.strftime("%Y-%m-%d")
	attendance = frappe.get_list("Biometric Attendance", filters={"user_id": user_id, "date":date , "punch":1}, fields=["*"])
	return attendance

def get_month_attendance(user_id):
	
	attendance = frappe.get_list("Biometric Attendance", filters={"user_id": user_id, "punch":0}, fields=["*"])
	
	return attendance

def get_month_attendance_log_out(user_id):
	
	attendance = frappe.get_list("Biometric Attendance", filters={"user_id": user_id, "punch":1}, fields=["*"])
	
	return attendance

def check_month_late(user_id,today,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	
	month_attendance = get_month_attendance(user_id)
	get_time = check_time_for_month(month_attendance,grade_details,start_time)

	return get_time
def check_month_late_for_total(user_id,today,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	
	month_attendance = get_month_attendance(user_id)
	get_time = check_time_for_month_total_minute(month_attendance,grade_details,start_time)

	return get_time

def check_month_late_without_p(user_id,today,grade_details,start_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	
	month_attendance = get_month_attendance(user_id)
	get_time = check_time_for_month_without_p(month_attendance,grade_details,start_time)

	return get_time

def check_month_late_log_out(user_id,today,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	
	month_attendance = get_month_attendance_log_out(user_id)
	get_time = check_time_log_out_for_month(month_attendance,grade_details,end_time)
	
	return get_time
def check_month_late_log_out_for_total(user_id,today,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	
	month_attendance = get_month_attendance_log_out(user_id)
	get_time = check_time_log_out_for_month_for_total(month_attendance,grade_details,end_time)
	
	return get_time
def check_month_late_log_out_without_p(user_id,today,grade_details,end_time):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	
	month_attendance = get_month_attendance_log_out(user_id)
	get_time = check_time_log_out_for_month_without_p(month_attendance,grade_details,end_time)
	
	return get_time

def sing_in_time_without_penalty(grade_details,start_time,today):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	#today = date.today()
	sing_in_without_penalty = grade_details[0]['sign_in_without_penalty']
	start_time_with_today_date = str(today)+" "+str(start_time)
	convert_start_time = datetime.datetime.strptime(start_time_with_today_date, '%Y-%m-%d %H:%M:%S')
	addition_of_time = ""
	if sing_in_without_penalty != 0:
		if sing_in_without_penalty < 60:
			
			addition_of_time = convert_start_time + timedelta(minutes=sing_in_without_penalty)  
			
		elif sing_in_without_penalty >= 60 and sing_in_without_penalty < 120:
				minute = sing_in_without_penalty - 60
				addition_of_time = convert_start_time + timedelta(hours = 1,minutes=minute) 
		elif sing_in_without_penalty >= 120 and sing_in_without_penalty < 180:
				minute = sing_in_without_penalty - 120
				addition_of_time = convert_start_time + timedelta(hours = 2,minutes=minute)
	else:
		addition_of_time = start_time_with_today_date
	return addition_of_time

def sing_in_time_with_penalty(grade_details,start_time,today):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	#today = date.today()
	sing_in_with_penalty = grade_details[0]['sign_in_with_penalty']
	start_time_with_today_date = str(today)+" "+str(start_time)
	convert_start_time = datetime.datetime.strptime(start_time_with_today_date, '%Y-%m-%d %H:%M:%S')
	addition_of_time = ""
	if sing_in_with_penalty != 0:
		if sing_in_with_penalty < 60:
			
			addition_of_time = convert_start_time + timedelta(minutes=sing_in_with_penalty)  
			
		elif sing_in_with_penalty >= 60 and sing_in_with_penalty < 120:
			minute = sing_in_with_penalty - 60
			addition_of_time = convert_start_time + timedelta(hours = 1,minutes=minute)
		elif  sing_in_with_penalty >= 120 and sing_in_with_penalty < 180:
			minute = sing_in_with_penalty - 120
			addition_of_time = convert_start_time + timedelta(hours = 2,minutes=minute)
	else:
		addition_of_time = start_time_with_today_date
	return addition_of_time
def sing_out_time_without_penalty(grade_details,end_time,today):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	#today = date.today()
	
	#sign_out_with_penalty = grade_details[0]['sign_out_with_penalty']
	sign_out_without_penalty = grade_details[0]['sign_out_without_penalty']
	start_time_with_today_date = str(today)+" "+str(end_time)
	convert_start_time = datetime.datetime.strptime(start_time_with_today_date, '%Y-%m-%d %H:%M:%S')
	addition_of_time = ""
	if sign_out_without_penalty != 0:
		if sign_out_without_penalty < 60:
			
			addition_of_time = convert_start_time - timedelta(minutes=sign_out_without_penalty)  
			
		elif sign_out_without_penalty >= 60 and sign_out_without_penalty < 120:
			minute = sign_out_without_penalty - 60
			addition_of_time = convert_start_time - timedelta(hours = 1,minutes=minute)

		elif sign_out_without_penalty >= 120 and sign_out_without_penalty < 180:
			minute = sign_out_without_penalty - 120
			addition_of_time = convert_start_time - timedelta(hours = 2,minutes=minute)
	else:
		addition_of_time = start_time_with_today_date
		
	return addition_of_time
def sing_out_time_with_penalty(grade_details,end_time,today):
	f= open("/home/frappe/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
	#today = date.today()
	sign_out_with_penalty = grade_details[0]['sign_out_with_penalty']
	start_time_with_today_date = str(today)+" "+str(end_time)
	convert_start_time = datetime.datetime.strptime(start_time_with_today_date, '%Y-%m-%d %H:%M:%S')
	addition_of_time = ""
	if sign_out_with_penalty != 0:
		if sign_out_with_penalty < 60:
			
			addition_of_time = convert_start_time - timedelta(minutes=sign_out_with_penalty)  
			
		elif sign_out_with_penalty >= 60 and sign_out_with_penalty < 120:
			minute = sign_out_with_penalty - 60
			addition_of_time = convert_start_time - timedelta(hours = 1,minutes=minute)

		elif sign_out_with_penalty >= 120 and sign_out_with_penalty < 180:
			minute = sign_out_with_penalty - 120
			addition_of_time = convert_start_time - timedelta(hours = 2,minutes=minute)
	else:
		addition_of_time = start_time_with_today_date
	return addition_of_time
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
def create_erp_attendance(doc, document):
	get_employee_details = frappe.get_list("Employee", filters={"name": doc.employee_id}, fields=["employee_name","company"])
	
	attendance_doc = frappe.new_doc("Attendance")
	attendance_doc.employee = doc.employee_id
	attendance_doc.status = doc.status
	attendance_doc.attendance_date = doc.date
	attendance_doc.save()
	attendance_doc.submit()
		
