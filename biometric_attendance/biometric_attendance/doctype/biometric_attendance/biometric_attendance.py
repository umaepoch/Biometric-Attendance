# -*- coding: utf-8 -*-
# Copyright (c) 2019, Akshay Mehta and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class BiometricAttendance(Document):
	pass

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
		attendance_doc.date = timestamp_date
		attendance_doc.source = device_name
		#attendance_doc.punch_status = "Before Lunch"
	
		attendance_doc.save()
		attendance_doc.submit()
		if attendance_doc.name:
			return "Success"
		else:
			return  False
