# -*- coding: utf-8 -*-
# Copyright (c) 2019, Akshay Mehta and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import json
import datetime

class BiometricAttendance(Document):
	pass
'''
@frappe.whitelist()
def add_log_based_on_employee_field():
	if frappe.request.data:
		reqData = json.loads(frappe.request.data)
		user_id = reqData.get("employee_field_value")
		device_name = reqData.get("device_id")
		timestamp = reqData.get("timestamp")
		log_type = reqData.get("log_type")
		attendance_doc = frappe.new_doc("Biometric Attendance")
		punch = 0
		Status = ""
		if log_type == "IN":
			punch = 0
			Status = "Check In"
		elif log_type == "OUT":
			punch = 1
			Status = "Check Out"
		else:
			punch = 10
			Status = "Unknown"
		attendance_doc.user_id = user_id
		attendance_doc.timestamp = timestamp
		attendance_doc.punch = punch
		attendance_doc.status = Status
		#attendance_doc.date = timestamp_date
		attendance_doc.source = device_name
		#attendance_doc.punch_status = "Before Lunch"
	
		attendance_doc.save()
		attendance_doc.submit()
		if attendance_doc.name:
			return "Success"
		else:
			return  False
'''
@frappe.whitelist()
def add_log_based_on_employee_field(employee_field_value, timestamp, device_id=None, log_type=None, skip_auto_attendance=0, employee_fieldname='attendance_device_id'):
    #f= open("/home/mmpy3/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
    #f.write("employee_field_value----------------"+str(employee_field_value)+'\n')
    #f.write("log_type----------------"+str(log_type)+'\n')
   
    """Finds the relevant Employee using the employee field value and creates a Employee Checkin.

    :param employee_field_value: The value to look for in employee field.
    :param timestamp: The timestamp of the Log. Currently expected in the following format as string: '2019-05-08 10:48:08.000000'
    :param device_id: (optional)Location / Device ID. A short string is expected.
    :param log_type: (optional)Direction of the Punch if available (IN/OUT).
    :param skip_auto_attendance: (optional)Skip auto attendance field will be set for this log(0/1).
    :param employee_fieldname: (Default: attendance_device_id)Name of the field in Employee DocType based on which employee lookup will happen.
    """

    if not employee_field_value or not timestamp:
        frappe.throw(_("'employee_field_value' and 'timestamp' are required."))
    
    employee = frappe.db.get_values("Employee", {employee_fieldname: employee_field_value}, ["name", "employee_name", employee_fieldname], as_dict=True)
    if employee:
        employee = employee[0]
    else:
        frappe.throw(_("No Employee found for the given employee field value. '{}': {}").format(employee_fieldname,employee_field_value))
    
    punch = 0
    Status = ""
    if log_type == "IN":
        punch = 0
        Status = "Check In"
    elif log_type == "OUT":
        punch = 1
        Status = "Check Out"
    else:
        punch = 10
        Status = "Unknown"
    date_time_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    time_date = date_time_obj.date()
    attendance_details = frappe.db.sql(""" select * from `tabBiometric Attendance` where users_id = %s and timestamp =%s and date= %s order by timestamp desc""",(employee_field_value,timestamp,time_date), as_dict=1 )
    #f.write("attendance_details----------------"+str(attendance_details)+'\n')
    if len(attendance_details) == 0:
	    attendance_doc = frappe.new_doc("Biometric Attendance")
	    attendance_doc.users_id = employee_field_value
	    attendance_doc.timestamp = timestamp
	    attendance_doc.punch = punch
	    attendance_doc.punch_status = Status
	    attendance_doc.date = time_date
	    attendance_doc.employee_id = employee.name
	    attendance_doc.user_name = employee.user_name
	    attendance_doc.source = device_id
	    attendance_doc.save()
	    attendance_doc.submit()

	    return "Success"
    else:
        return "Failed"


#suresh_changes
@frappe.whitelist()
def get_proper_dat_time(date_str):
	converted_date = datetime.datetime.strptime( date_str, '%Y-%m-%d %H:%M:%S')
	return get_formatted()

@frappe.whitelist()
def get_full_user_name(employee_user_id):
	user_full_name = frappe.db.get_value("User", {"name":employee_user_id},"full_name")
	return user_full_name

@frappe.whitelist()
def get_punch_status_list():
	punch_status_temp_list=[]
	punch_status_list = frappe.db.sql("""select punch_type,punch_no from `tabPunch Child` where parent  ='P-S-00001'""",as_dict=1)
	for punch_status in punch_status_list:
		punch_status_temp_list.append(punch_status["punch_type"])
	return punch_status_temp_list

@frappe.whitelist()
def get_punch_status_code(punch_status):
	punch_status_list = get_punch_status_list_adv()
	punch_status_code_temp= "hello"
	if punch_status_list:
		for punch_status_row in punch_status_list:
			if punch_status_row["punch_type"] == punch_status :
				punch_status_code_temp = punch_status_row["punch_no"]
				return punch_status_code_temp
	return punch_status_code_tem

def get_punch_status_list_adv():
	punch_status_list = frappe.db.sql("""select punch_type,punch_no from `tabPunch Child` where parent  ='P-S-00001'""",as_dict=1)
	return punch_status_list

@frappe.whitelist()
def get_employee_id(user_id):
	#print "reqData",reqData
	user_email = frappe.db.get_value("User", {"name":user_id},"name")
	#print "user_email",user_email
	employee_id = frappe.db.get_value("Employee", {"user_id":user_email},"name")
	#print "employee_id",employee_id
	if(employee_id):
		return employee_id
	else:
		return 0


	    
    
