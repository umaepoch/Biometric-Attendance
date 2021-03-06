# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate
from frappe import _, msgprint
from frappe.model.mapper import get_mapped_doc
from datetime import datetime
import datetime
from datetime import date, timedelta
import calendar
import dateutil.parser
import time
import math
import json
import ast

def execute(filters=None):
	columns, data = [], []
	branch = filters.get("branch")
	department = filters.get("department")
	employee = filters.get("reports_to")
	date = filters.get("date")
	columns = get_columns()
	details = get_attendance_details(employee,date,filters)
	prepare_details = get_prepare_details(details)
	check_in = frappe.get_list("Punch Child",filters={"punch_type":"Check In"}, fields=["punch_no"])
	check_out = frappe.get_list("Punch Child",filters={"punch_type":"Check Out"}, fields=["punch_no"])
	lunch_out = frappe.get_list("Punch Child",filters={"punch_type":"Lunch Out"}, fields=["punch_no"])
	lunch_in = frappe.get_list("Punch Child",filters={"punch_type":"Lunch In"}, fields=["punch_no"])
	pto_in = frappe.get_list("Punch Child",filters={"punch_type":"PTO In"}, fields=["punch_no"])
	pto_out = frappe.get_list("Punch Child",filters={"punch_type":"PTO Out"}, fields=["punch_no"])
	current_datetime  = frappe.utils.data.now_datetime()
	current_time = current_datetime.strftime("%H:%M:%S")
	datetime_al = str(date)+" "+str(current_time)
	convert = datetime.datetime.strptime(datetime_al, '%Y-%m-%d %H:%M:%S')
	if employee:
		i = 0
		total_pots = 0
		validates = False
		lunch_missed_in = False
		lunch_missed_out = False
		check_out_timestamp = ""
		check_in_timestamp = ""
		lunch_out_timestamp = ""
		lunch_in_timestamp = ""
		pto_out_timestamp= ""
		pto_in_timestamp = ""
		location = ""
		status_id = ""
		if len(details) != 0:
			for pre in details:
				if pre.punch == check_in[0]['punch_no']:
					check_in_timestamp = pre.timestamp
				elif pre.punch == check_out[0]['punch_no']:
					check_out_timestamp =  pre.timestamp
				elif pre.punch == lunch_in[0]['punch_no']:
					lunch_in_timestamp =  pre.timestamp
				elif pre.punch == lunch_out[0]['punch_no']:
					lunch_out_timestamp =  pre.timestamp
				elif pre.punch == pto_out[0]['punch_no']:
					pto_out_timestamp =  pre.timestamp
				
				elif pre.punch == pto_in[0]['punch_no']:
					i +=1
					pto_in_timestamp =  pre.timestamp
				if pto_out_timestamp != "" and pto_in_timestamp != "":
					total_pot = pto_in_timestamp - pto_out_timestamp
					seconds = total_pot.seconds
					total_pots += seconds
				
					pto_out_timestamp = ""
					pto_in_timestamp = ""
				
				status = get_status(employee,date)
				
				if status[0].punch_status == "Check In" or status[0].punch_status == "Lunch In" or status[0].punch_status == "PTO In":
					status_id = "At Work"
				elif status[0].punch_status == "Lunch Out":
					status_id = "At Lunch"
				elif status[0].punch_status == "PTO Out":
					status_id = "PTO"
				elif status[0].punch_status == "Check Out":
					status_id = "Signed out for the day"
			employee_name = frappe.get_list("Employee", filters={"name":employee},fields=[ "employee_name","branch","department"])
			if check_out_timestamp == "":
				datetime_end = str(date)+" 23:59:59"
				convert_end = datetime.datetime.strptime(datetime_end, '%Y-%m-%d %H:%M:%S')
				if current_datetime >= convert_end:
					check_out_timestamp = convert_end
					status_id = "Signed out for the day"
			if check_out_timestamp != "" and check_in_timestamp != "":
				if pto_out_timestamp == "" and pto_in_timestamp == "":
					pass
				else:
					validates = True
				total_lunch = ""
				if lunch_in_timestamp != "" and lunch_out_timestamp != "":
					total_lunch = lunch_in_timestamp - lunch_out_timestamp 
				elif lunch_in_timestamp == "" and lunch_out_timestamp != "":
					validates = True
				
				elif lunch_in_timestamp != "" and lunch_out_timestamp == "":
					validates = True
				total = check_out_timestamp - check_in_timestamp
			
				total_working = ""
				if total_lunch != "":
					total_working = total - total_lunch
				else:
					total_working = total
				if lunch_in_timestamp == "" and lunch_out_timestamp != "":
					one_hour_less = datetime.timedelta(seconds = 3600)
					total_working -= one_hour_less
				if lunch_in_timestamp != "" and lunch_out_timestamp == "":
					one_hour_less = datetime.timedelta(seconds = 3600)
					total_working -= one_hour_less
		
				converted = datetime.timedelta(seconds = total_pots)
				if total_working != "":
			
					total_worked = total_working - converted
			elif check_out_timestamp == "" and check_in_timestamp != "":
				validates = True
				total_worked = ""
				if lunch_in_timestamp == "" and lunch_out_timestamp != "":
					total_worked = lunch_out_timestamp - check_in_timestamp
					validates = True
				elif lunch_in_timestamp != "" and lunch_out_timestamp != "":
					lunch_break = lunch_in_timestamp - lunch_out_timestamp
					total_worked = convert - check_in_timestamp
					total_worked -= lunch_break
				if pto_out_timestamp == "" and pto_in_timestamp == "":
					if total_pots != "":
						converted = datetime.timedelta(seconds = total_pots)
						if total_worked != "":
							total_worked -= converted
						elif total_worked == "":
							total_worked = convert - check_in_timestamp
							total_worked -= converted
				elif pto_out_timestamp != "" and pto_in_timestamp == "":
					validates = True
					if total_pots != "":
						converted = datetime.timedelta(seconds = total_pots)
						if total_worked != "":
							#total_worked -= converted
							total_worked = pto_out_timestamp - check_in_timestamp
							pto_time = convert - pto_out_timestamp
							converted += pto_time
							total_worked -= converted
					
							
					elif total_pots == "":
						
						pto_time = convert - pto_out_timestamp 
						if total_worked != "":
							total_worked -= pto_time
						elif total_worked == "":
							total_worked = pto_out_timestamp - check_in_timestamp
							total_worked -= pto_time
			complete = ""
			if validates == True:
				complete = 'No'
			else:
				complete = 'Yes'
			data.append([employee_name[0]['employee_name'], employee,status_id,check_in_timestamp,lunch_out_timestamp,lunch_in_timestamp,check_out_timestamp,converted,i,complete, employee_name[0]['department'],employee_name[0]['branch']])
	else:
		attendance = get_attendance_list(branch,department,date)
		prepare_attendace = get_prepare_attendance(attendance)
		for ds in prepare_attendace:
			i =0
			total_pots = 0
			validates = False
			lunch_missed_in = False
			lunch_missed_out = False
			check_out_timestamp = ""
			check_in_timestamp = ""
			lunch_out_timestamp = ""
			lunch_in_timestamp = ""
			pto_out_timestamp= ""
			pto_in_timestamp = ""
			location = ""
			converted = ""
			total_worked = ""
			attendance_details = prepare_attendace[ds]
			status = get_status(ds,date)
			status_id = ""
			if status[0].punch_status == "Check In" or status[0].punch_status == "Lunch In" or status[0].punch_status == "PTO In":
				status_id = "At Work"
			elif status[0].punch_status == "Lunch Out":
				status_id = "At Lunch"
			elif status[0].punch_status == "PTO Out":
				status_id = "PTO"
			elif status[0].punch_status == "Check Out":
				status_id = "Signed out for the day"
			
			for pre in attendance_details:
				if pre['punch'] == check_in[0]['punch_no']:
					check_in_timestamp = pre['timestamp']
				elif pre['punch'] == check_out[0]['punch_no']:
					check_out_timestamp =  pre['timestamp']
				elif pre['punch'] == lunch_in[0]['punch_no']:
					lunch_in_timestamp =  pre['timestamp']
				elif pre['punch'] == lunch_out[0]['punch_no']:
					lunch_out_timestamp =  pre['timestamp']
				elif pre['punch'] == pto_out[0]['punch_no']:
					pto_out_timestamp =  pre['timestamp']
				
				elif pre['punch'] == pto_in[0]['punch_no']:
					i +=1
					pto_in_timestamp =  pre['timestamp']
				
				if pto_out_timestamp != "" and pto_in_timestamp != "":
					
					total_pot = pto_in_timestamp - pto_out_timestamp
					seconds = total_pot.seconds
					
					total_pots += seconds
				
					pto_out_timestamp = ""
					pto_in_timestamp = ""
			
			employee_name = frappe.get_list("Employee", filters={"name": ds}, fields=["employee_name", "department","branch"])
			total = ""
			if check_out_timestamp == "":
				datetime_end = str(date)+" 23:59:59"
				convert_end = datetime.datetime.strptime(datetime_end, '%Y-%m-%d %H:%M:%S')
				if current_datetime >= convert_end:
					check_out_timestamp = convert_end
					status_id = "Signed out for the day"
			if check_out_timestamp != "" and check_in_timestamp != "":
				if pto_out_timestamp == "" and pto_in_timestamp == "":
					pass
				else:
					validates = True
				total_lunch = ""
				if lunch_in_timestamp != "" and lunch_out_timestamp != "":
					total_lunch = lunch_in_timestamp - lunch_out_timestamp 
				elif lunch_in_timestamp == "" and lunch_out_timestamp != "":
					validates = True
				
				elif lunch_in_timestamp != "" and lunch_out_timestamp == "":
					validates = True
				total = check_out_timestamp - check_in_timestamp
			
				total_working = ""
				if total_lunch != "":
					total_working = total - total_lunch
				else:
					total_working = total
				if lunch_in_timestamp == "" and lunch_out_timestamp != "":
					one_hour_less = datetime.timedelta(seconds = 3600)
					total_working -= one_hour_less
				if lunch_in_timestamp != "" and lunch_out_timestamp == "":
					one_hour_less = datetime.timedelta(seconds = 3600)
					total_working -= one_hour_less
		
				converted = datetime.timedelta(seconds = total_pots)
				if total_working != "":
			
					total_worked = total_working - converted
			elif check_out_timestamp == "" and check_in_timestamp != "":
				validates = True
				total_worked = ""
				if lunch_in_timestamp == "" and lunch_out_timestamp != "":
					total_worked = lunch_out_timestamp - check_in_timestamp
					
					validates = True
				elif lunch_in_timestamp != "" and lunch_out_timestamp != "":
					lunch_break = lunch_in_timestamp - lunch_out_timestamp
					total_worked = convert - check_in_timestamp
					total_worked -= lunch_break
				if pto_out_timestamp == "" and pto_in_timestamp == "":
					if total_pots != "":
						converted = datetime.timedelta(seconds = total_pots)
						if total_worked != "":
							total_worked -= converted
						elif total_worked == "":
							total_worked = convert - check_in_timestamp
							total_worked -= converted
				elif pto_out_timestamp != "" and pto_in_timestamp == "":
					validates = True
					if total_pots != 0:
						converted = datetime.timedelta(seconds = total_pots)
						if total_worked != "":
							#total_worked -= converted
							total_worked = pto_out_timestamp - check_in_timestamp
							pto_time = convert - pto_out_timestamp
							converted += pto_time
							total_worked -= converted
						elif total_worked == "": 
							pto_time = convert - pto_out_timestamp
							total_worked = pto_out_timestamp - check_in_timestamp
							total_worked -= pto_time
							converted += pto_time
							
					elif total_pots == 0:
						
						pto_time = convert - pto_out_timestamp
						converted = pto_time
						if total_worked != "":
							total_worked -= pto_time
						elif total_worked == "":
							total_worked = pto_out_timestamp - check_in_timestamp
							total_worked -= pto_time
							
			complete = ""
			if validates == True:
				complete = 'No'
			else:
				complete = 'Yes'
			data.append([employee_name[0]['employee_name'], ds,status_id,check_in_timestamp,
					lunch_out_timestamp,lunch_in_timestamp,check_out_timestamp,converted,i,complete,
					employee_name[0]['department'],employee_name[0]['branch']])

	return columns, data

def get_columns():
	return [
		_("Employee Name") + "::150",
		_("Employee ID") + ":Link/Employee:150",
		_("Current Status") + "::150",
		_("Check In") + "::150",
		_("Lunch Out") + "::180",
		_("Lunch In") + "::150",
		_("Check Out") + "::150",
		_("Total PTO Time Taken") + "::150",
		_("Number of PTOs") + "::150",
		_("Complete In and out") + "::200",
		_("Department") + "::150",
		_("Branch") + "::150"
		]
def get_attendance_details(employee,date,filters):
	branch = filters.get("branch")
	department = filters.get("department")
	if branch is not None and department is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date= %s and b.docstatus=1 and e.branch = %s and e.department = %s order by  b.name""",(employee,date,branch,department),as_dict=1)
	elif branch is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date= %s and b.docstatus=1 and e.branch = %s order by  b.name""",(employee,date,branch),as_dict=1)
	elif department is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date= %s and b.docstatus=1 and e.department = %s order by  b.name""",(employee,date,department),as_dict=1)
	else:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date= %s and b.docstatus=1  order by  b.name""",(employee,date),as_dict=1)
	return attendance
def get_prepare_details(details):
	
	pto_in = frappe.get_list("Punch Child",filters={"punch_type":"PTO In"}, fields=["punch_no"])
	pto_out = frappe.get_list("Punch Child",filters={"punch_type":"PTO Out"}, fields=["punch_no"])
	#print "details-------------",details
	data = []
	i =0
	for d in details:
		if d['punch'] == pto_out[0]['punch_no']:
			data.append({"pto_out": d['timestamp']})
		elif d['punch'] == pto_in[0]['punch_no']:
			i +=1
			data.append({"pto_in": d['timestamp'], "no_of_time": i})
			#print "i-------------",i
	return data
def get_attendance_list(branch,department,date):
	if branch is not None and department is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b , `tabEmployee` e where e.name = b.employee_id and e.branch = %s and e.department = %s and b.date = %s and b.docstatus=1""", (branch,department,date), as_dict=1)
	elif branch is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b , `tabEmployee` e where e.name = b.employee_id and e.branch = %s  and b.date = %s and b.docstatus=1""", (branch,date), as_dict=1)
	elif department is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b , `tabEmployee` e where e.name = b.employee_id and e.department = %s  and b.date = %s and b.docstatus=1""", (department,date), as_dict=1)
	else:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance`  where date = %s and docstatus =1""", date, as_dict=1)
	return attendance

def get_prepare_attendance(attendance):
	data = {}
	for d in attendance:
		if d.employee_id:
			key = d.employee_id
			if len(data) != 0:
				if key in data:
					data[key].append({"user_name": d.user_name, "location":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.source})
				else:
					data[key]=[{"user_name": d.user_name, "location":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.source}]
			else:
				data[key]=[{"user_name": d.user_name, "location":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.source}]
	return data
def get_status(employee,date):
	status = frappe.db.sql("""select * from `tabBiometric Attendance` where employee_id = %s and date =%s order by name desc limit 1 """,(employee,date), as_dict=1)
	return status
