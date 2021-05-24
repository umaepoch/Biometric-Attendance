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
	
	attendance = fetching_previous_day_attendance_details(filters)
	#print("atttendance",attendance)
	employee_checkin=fetching_checkin_attendance_details(filters)
	#print("employee_checkin",employee_checkin)
	result_set=attendance+employee_checkin
	#print("combined dict",result_set)
	prepare_attendace = get_prepare_attendance_1(result_set)
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
		check_in_source=""
		check_in_location_name=""
		check_out_source=""
		check_out_location_name=""
		#print("--------",prepare_attendace[ds][0]['empployee_id'])
		attendance_details = prepare_attendace[ds]
		#print("attendence_details",attendance_details)
		#print("attendance_details lenght",len(attendance_details))
	
		if (len(attendance_details)==2):
			#print("+++++++++++++++++++++++=========")
			if ( (attendance_details[0]['punch']==attendance_details[1]['punch']==1) ):
				latest = max(attendance_details[0]['timestamp'], attendance_details[1]['timestamp']) # t1, in this case
				#print(latest)
				if latest==attendance_details[0]['timestamp']:
					del attendance_details[1]
					#print("----if")
				else:
					del attendance_details[0]
					#print("----else")
			#print(attendance_details)
			
		if (len(attendance_details)==2):	   
			if ((attendance_details[0]['punch']==attendance_details[1]['punch']==0) ):
				latest = min(attendance_details[0]['timestamp'], attendance_details[1]['timestamp']) # t1, in this case
				#print(latest)
				if latest==attendance_details[0]['timestamp']:
					del attendance_details[1]
					#print("----if")
				else:
					del attendance_details[0]
					#print("----else")
			
	
		if (len(attendance_details)==3):
			#print("entered in 3")
			if ( (attendance_details[0]['punch']==attendance_details[1]['punch']==0) ):
				latest = min(attendance_details[0]['timestamp'], attendance_details[0]['timestamp']) # t1, in this case
				#print("both 0 and 1 are in",latest)
				if latest==attendance_details[0]['timestamp']:
					del attendance_details[1]
					#print("----if")
				else:
					del attendance_details[0]
					#print("----else")
		if (len(attendance_details)==3):	
			if attendance_details[0]['punch']==attendance_details[2]['punch']==0:
				latest = min(attendance_details[0]['timestamp'], attendance_details[2]['timestamp']) # t1, in this case
				#print("both 0 and 2 are in",latest)
				if latest==attendance_details[0]['timestamp']:
					del attendance_details[2]
					#print("----if")
				else:
					del attendance_details[0]
					#print("----else")
			   
		if (len(attendance_details)==3):
			#print("entered in 3 out")
			if ( (attendance_details[1]['punch']==attendance_details[2]['punch']==1) ):
				latest = max(attendance_details[1]['timestamp'], attendance_details[2]['timestamp']) # t1, in this case
				#print("both 1 and 2 are out",latest)
				if latest==attendance_details[1]['timestamp']:
					del attendance_details[2]
					#print("----if")
				else:
					del attendance_details[1]
					#print("----else")
		if (len(attendance_details)==3):
			if ( (attendance_details[0]['punch']==attendance_details[2]['punch']==1) ):
				latest = max(attendance_details[0]['timestamp'], attendance_details[2]['timestamp']) # t1, in this case
				#print("both 0 and 2 are out",latest)
				if latest==attendance_details[0]['timestamp']:
					del attendance_details[2]
					#print("----if")
				else:
					del attendance_details[0]
					#print("----else")
		
		if (len(attendance_details)==4):
			#print("enterd in length 4")
			if ( (attendance_details[1]['punch']==attendance_details[3]['punch']==1) ):
				latest = max(attendance_details[1]['timestamp'], attendance_details[3]['timestamp']) # t1, in this case
				#print("entered in logout",latest)
				if latest==attendance_details[1]['timestamp']:
					del attendance_details[3]
					#print("----if")
				else:
					del attendance_details[1]
					#print("----else")
			#print(attendance_details)
		if (len(attendance_details)==4):	   
			if ((attendance_details[0]['punch']==attendance_details[2]['punch']==0) ):
				#print("entered in if login")
				latest = min(attendance_details[0]['timestamp'], attendance_details[2]['timestamp']) # t1, in this case
				#print("login",latest)
				if latest==attendance_details[0]['timestamp']:
					del attendance_details[2]
					#print("----if")
				else:
					del attendance_details[0]
					#print("----else")
			#print("final",attendance_details)	   
		
		for pre in attendance_details:
			if pre['punch'] == check_in[0]['punch_no'] or  pre['punch_status'] == "IN":
				check_in_timestamp = pre['timestamp']
				check_in_source=pre['source']
				check_in_location_name=pre['location_name']
			elif pre['punch'] == check_out[0]['punch_no'] or pre['punch_status'] == "OUT":
				check_out_timestamp =  pre['timestamp']
				check_out_source=pre['source']
				check_out_location_name=pre['location_name']
		employee_name = frappe.get_list("Employee", filters={"name":prepare_attendace[ds][0]['empployee_id']}, fields=["employee_name", "department","branch"])
		#print("employee_name",employee_name)
		if len(attendance_details)>1:
			data.append([employee_name[0]['employee_name'],prepare_attendace[ds][0]['empployee_id'],
		attendance_details[0]['timestamp'].strftime("%d-%m-%Y"),check_in_timestamp,
		check_in_source,check_in_location_name,check_out_timestamp,check_out_source,check_out_location_name,
		employee_name[0]['department'],employee_name[0]['branch']])
		else:
			data.append([employee_name[0]['employee_name'],prepare_attendace[ds][0]['empployee_id'],
		attendance_details[0]['timestamp'].strftime("%d-%m-%Y"),check_in_timestamp,
		check_in_source,check_in_location_name,check_out_timestamp,"","",
		employee_name[0]['department'],employee_name[0]['branch']])

	return columns, data


def get_columns():
    	return [
		_("Employee Name") + "::150",
		_("Employee ID") + ":Link/Employee:150",
		_("Date") + "::150",
		_("Check In") + "::150",
		_("Check In Source") + "::150",
		_("Check In Location") + "::150",
		_("Check out") + "::150",
		_("Check out Source") + "::150",
		_("Check out Location") + "::150",
		_("Department") + "::150",
		_("Branch") + "::150"
		]


def fetching_previous_day_attendance_details(filters):
    condition = get_conditions(filters)
    sql_str = frappe.db.sql("""select e.employee_name,b.employee_id,b.timestamp as date,b.punch_status,b.punch,"m@tendance" as doc_source,b.timestamp as timestamp,b.location_name,e.department,e.branch from `tabBiometric Attendance` b , `tabEmployee` e where e.name = b.employee_id and  b.docstatus=1
 %s  """ %
		condition, as_dict=1)
	#print("sql",sql_str)
    return sql_str 

def fetching_checkin_attendance_details(filters):
    condition = get_employee_checkin_condition(filters)
    sql_str = frappe.db.sql("""select eci.employee_name,eci.employee as employee_id,eci.time as date,eci.time as timestamp,"Employee Check In/Out" as doc_source,"" as location_name,eci.log_type as punch_status,if(eci.log_type="IN",0,1) as punch,e.department,e.branch  from `tabEmployee Checkin` eci , `tabEmployee` e where e.name = eci.employee
 %s  """ %
		condition, as_dict=1)
	#print("sql",sql_str)
    return sql_str 


def get_conditions(filters):
	conditions=""
	#print("enterd in condition")
	if filters.get("from_date"):
		conditions +='and DATE_FORMAT(b.timestamp, "%%Y-%%m-%%d") >= %s'   % frappe.db.escape(filters.get("from_date"), percent=False)
	if filters.get("to_date"):
		conditions += 'and DATE_FORMAT(b.timestamp, "%%Y-%%m-%%d") <= %s' % frappe.db.escape(filters.get("to_date"), percent=False)
	if filters.get("department"):
		conditions += 'and e.department = %s' % frappe.db.escape(filters.get("department"), percent=False)
	if filters.get("branch"):
		conditions += 'and e.branch = %s' % frappe.db.escape(filters.get("branch"), percent=False)
	if filters.get("reports_to"):
		conditions += 'and e.reports_to= %s' % frappe.db.escape(filters.get("reports_to"), percent=False)
	return conditions

def get_employee_checkin_condition(filters):
	conditions=""
	#print("enterd in condition")
	if filters.get("from_date"):
		conditions += 'and DATE_FORMAT(eci.time, "%%Y-%%m-%%d") >= %s'  % frappe.db.escape(filters.get("from_date"), percent=False)
	if filters.get("to_date"):
		conditions += 'and DATE_FORMAT(eci.time, "%%Y-%%m-%%d") <= %s' % frappe.db.escape(filters.get("to_date"), percent=False)
	if filters.get("department"):
		conditions += 'and e.department = %s' % frappe.db.escape(filters.get("department"), percent=False)
	if filters.get("branch"):
		conditions += 'and e.branch = %s' % frappe.db.escape(filters.get("branch"), percent=False)
	if filters.get("reports_to"):
		conditions += 'and e.reports_to= %s' % frappe.db.escape(filters.get("reports_to"), percent=False)
	return conditions

def get_prepare_attendance_1(result_set):
	data = {}
	for d in result_set:
		if d.employee_id:
			key = d.employee_id+"-"+d.timestamp.strftime("%d-%m-%Y")
			#print("key----------",key)
			if len(data) != 0:
				if key in data:
					data[key].append({"user_name": d.user_name, "location_name":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.doc_source})
				else:
					data[key]=[{"user_name": d.user_name, "location_name":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.doc_source}]
			else:
				data[key]=[{"user_name": d.user_name, "location_name":d.location_name, "punch_status": d.punch_status, "punch":d.punch, "timestamp":d.timestamp, "empployee_id":d.employee_id, "source":d.doc_source}]
		#print("--------",data)
	return data










    
