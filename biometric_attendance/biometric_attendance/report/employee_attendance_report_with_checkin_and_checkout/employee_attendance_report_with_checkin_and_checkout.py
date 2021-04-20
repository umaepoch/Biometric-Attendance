# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from os import O_DSYNC
import frappe
from frappe.utils import data, flt, getdate
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

data = []
def execute(filters=None):
	columns, data = [], []
	branch = filters.get("branch")
	department = filters.get("department")
	employee = filters.get("reports_to")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	columns = get_columns()
	check_in = frappe.get_list("Punch Child",filters={"punch_type":"Check In"}, fields=["punch_no"])
	#print("check_in",check_in)
	check_out = frappe.get_list("Punch Child",filters={"punch_type":"Check Out"}, fields=["punch_no"])
	lunch_out = frappe.get_list("Punch Child",filters={"punch_type":"Lunch Out"}, fields=["punch_no"])
	lunch_in = frappe.get_list("Punch Child",filters={"punch_type":"Lunch In"}, fields=["punch_no"])
	pto_in = frappe.get_list("Punch Child",filters={"punch_type":"PTO In"}, fields=["punch_no"])
	pto_out = frappe.get_list("Punch Child",filters={"punch_type":"PTO Out"}, fields=["punch_no"])
	current_datetime  = frappe.utils.data.now_datetime()
	current_time = current_datetime.strftime("%H:%M:%S")
	datetime_al = str(from_date)+" "+str(current_time)
	convert = datetime.datetime.strptime(datetime_al, '%Y-%m-%d %H:%M:%S')
	details = get_attendance_details(employee,from_date,to_date,filters)
	#print("details",details)
	prepare_details = get_prepare_details(details)
	#print("prepare_details",prepare_details)
	
	
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

				status = get_status(employee,filters)

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
				datetime_end = str(to_date)+" 23:59:59"
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
			if len(details)>1:
				data.append([employee_name[0]['employee_name'],employee,details[0]['date'].strftime("%d-%m-%Y"),status_id,check_in_timestamp,
					details[0]['source'],check_out_timestamp,details[1]['source'],complete,
					employee_name[0]['department'],employee_name[0]['branch']])
			else:
				data.append([employee_name[0]['employee_name'],employee,details[0]['date'].strftime("%d-%m-%Y"),status_id,check_in_timestamp,
					details[0]['source'],check_out_timestamp,"",complete,
					employee_name[0]['department'],employee_name[0]['branch']])
    				
	else:
		attendance = fetching_previous_day_attendance_details(filters)
		prepare_attendace = get_prepare_attendance(attendance)
		#print("prepare_attendence",prepare_attendace)
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
			#print("attendence_details",attendance_details)
			#print("ds",ds)
			status = get_status(ds,filters)
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
				datetime_end = str(to_date)+" 23:59:59"
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
			if len(attendance_details)>1:
				data.append([employee_name[0]['employee_name'],ds,attendance_details[0]['date'].strftime("%d-%m-%Y"),status_id,check_in_timestamp,
						attendance_details[0]['source'],check_out_timestamp,attendance_details[1]['source'],complete,
						employee_name[0]['department'],employee_name[0]['branch']])	
			else:
					
				data.append([employee_name[0]['employee_name'],ds,attendance_details[0]['date'].strftime("%d-%m-%Y"),status_id,check_in_timestamp,
					attendance_details[0]['source'],check_out_timestamp,"",complete,
					employee_name[0]['department'],employee_name[0]['branch']])	

		

	return columns, data


def get_columns():
    	return [
		_("Employee Name") + "::150",
		_("Employee ID") + ":Link/Employee:150",
		_("Date") + "::150",
		_("Current Status") + "::150",
		_("Check In") + "::150",
		_("Check In Source") + "::150",
		_("Check Out") + "::150",
		_("Check Out Source") + "::150",
		_("Complete In and out") + "::200",
		_("Department") + "::150",
		_("Branch") + "::150"
		]


def fetching_previous_day_attendance_details(filters):
    condition = get_conditions(filters)
    sql_str = frappe.db.sql("""select * from `tabBiometric Attendance` b , `tabEmployee` e where e.name = b.employee_id
 %s  """ %
		condition, as_dict=1)
	#print("sql",sql_str)
    return sql_str 


def get_conditions(filters):
	conditions=""
	#print("enterd in condition")
	if filters.get("from_date"):
		conditions += 'and b.date >= %s'  % frappe.db.escape(filters.get("from_date"), percent=False)
	if filters.get("to_date"):
		conditions += 'and b.date <= %s' % frappe.db.escape(filters.get("to_date"), percent=False)
	if filters.get("department"):
		conditions += 'and e.department = %s' % frappe.db.escape(filters.get("department"), percent=False)
	if filters.get("branch"):
		conditions += 'and e.branch = %s' % frappe.db.escape(filters.get("branch"), percent=False)
	if filters.get("reports_to"):
		conditions += 'and b.employee_id = %s' % frappe.db.escape(filters.get("reports_to"), percent=False)
	return conditions

def get_prepare_attendance(attendance):
	data = {}
	for d in attendance:
		if d.employee_id:
			key = d.employee_id
			if len(data) != 0:
				if key in data:
					data[key].append({"user_name": d.user_name, "location":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.source, "date":d.date})
				else:
					data[key]=[{"user_name": d.user_name, "location":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.source, "date":d.date}]
			else:
				data[key]=[{"user_name": d.user_name, "location":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.source, "date":d.date}]
			#print(data)
	return data

def get_status(employee,filters):
	#condition = get_conditions_of_status(filters)
	from_date=filters.get("from_date")
	to_date=filters.get("to_date")
	if from_date is not None:
		status = frappe.db.sql("""select * from `tabBiometric Attendance` where employee_id = %s  and date >=%s order by name desc limit 1 """,(employee,from_date), as_dict=1)
	elif to_date is not None:
		status = frappe.db.sql("""select * from `tabBiometric Attendance` where employee_id = %s  and date <=%s order by name desc limit 1 """,(employee,to_date), as_dict=1)
	#print("status",status)
	return status

def get_attendance_details(employee,from_date,to_date,filters):
	branch = filters.get("branch")
	department = filters.get("department")
	
	if branch is not None and department is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date>= %s and b.date<= %s and b.docstatus=1 and e.branch = %s and e.department = %s order by  b.name""",(employee,from_date,to_date,branch,department),as_dict=1)
	elif branch is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date>= %s and b.date<= %s and b.docstatus=1 and e.branch = %s order by  b.name""",(employee,from_date,to_date,branch),as_dict=1)
	elif department is not None:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date>= %s and b.date<= %s and b.docstatus=1 and e.department = %s order by  b.name""",(employee,from_date,to_date,department),as_dict=1)
	else:
		attendance = frappe.db.sql("""select * from `tabBiometric Attendance` b, `tabEmployee` e where e.name = b.employee_id and b.employee_id = %s  and b.date>= %s and b.date<= %s and b.docstatus=1  order by  b.name""",(employee,from_date,to_date),as_dict=1)
	return attendance



def get_prepare_details(details):
	
	pto_in = frappe.get_list("Punch Child",filters={"punch_type":"PTO In"}, fields=["punch_no"])
	pto_out = frappe.get_list("Punch Child",filters={"punch_type":"PTO Out"}, fields=["punch_no"])
	#print ("details-------------",details)
	data = []
	i =0
	for d in details:
		if d['punch'] == pto_out[0]['punch_no']:
			data.append({"pto_out": d['timestamp']})
		elif d['punch'] == pto_in[0]['punch_no']:
			i +=1
			data.append({"pto_in": d['timestamp'], "no_of_time": i})
			#print ("i-------------",i)
	return data
