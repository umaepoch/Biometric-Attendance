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
    f= open("/home/mmpy3/frappe-bench/apps/biometric_attendance/biometric_attendance/biometric_attendance/output.out","a+")
    f.write("employee_field_value----------------"+str(employee_field_value)+'\n')
    f.write("log_type----------------"+str(log_type)+'\n')
   
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
    f.write("attendance_details----------------"+str(attendance_details)+'\n')
    if len(attendance_details) == 0:
	    attendance_doc = frappe.new_doc("Biometric Attendance")
	    attendance_doc.users_id = employee_field_value
	    attendance_doc.timestamp = timestamp
	    attendance_doc.punch = punch
	    attendance_doc.status = Status
	    attendance_doc.date = time_date
	    attendance_doc.employee_id = employee.name
	    attendance_doc.user_name = employee.user_name
	    attendance_doc.source = device_id
	    attendance_doc.save()
	    attendance_doc.submit()
	    if attendance_doc.name:
                return "Success"
	    else:
                return  "Fail"
   else:
	return "Fail"
