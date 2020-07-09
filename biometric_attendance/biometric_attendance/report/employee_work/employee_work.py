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
	details = get_attendance_details(employee,date)
	prepare_details = get_prepare_details(details)
	print "prepare_details-------------",prepare_details
	check_in = frappe.get_list("Punch Child",filters={"punch_type":"Check In"}, fields=["punch_no"])
	check_out = frappe.get_list("Punch Child",filters={"punch_type":"Check Out"}, fields=["punch_no"])
	lunch_out = frappe.get_list("Punch Child",filters={"punch_type":"Lunch Out"}, fields=["punch_no"])
	lunch_in = frappe.get_list("Punch Child",filters={"punch_type":"Lunch In"}, fields=["punch_no"])
	pto_in = frappe.get_list("Punch Child",filters={"punch_type":"PTO In"}, fields=["punch_no"])
	pto_out = frappe.get_list("Punch Child",filters={"punch_type":"PTO Out"}, fields=["punch_no"])
	check_out_timestamp = ""
	check_in_timestamp = ""
	lunch_out_timestamp = ""
	lunch_in_timestamp = ""
	pto_out_timestamp= ""
	pto_in_timestamp = ""
	i = 0
	total_pots = 0
	location = ""
	if len(details) != 0:
		for pre in details:
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
				print "pto_out_timestamp------------",pto_out_timestamp
				print "pto_in_timestamp------------",pto_in_timestamp
				total_pot = pto_in_timestamp - pto_out_timestamp
				seconds = total_pot.seconds
				total_pots += seconds
				
				pto_out_timestamp = ""
				pto_in_timestamp = ""
			if pre['source'] == "Mobile":
				location = "home"
			else:
				location = "Office"
			
		total_lunch = ""
		if lunch_in_timestamp != "" and lunch_out_timestamp != "":
			total_lunch = lunch_in_timestamp - lunch_out_timestamp 
	
		total = ""
		if check_out_timestamp != "" and check_in_timestamp != "":
			total = check_out_timestamp - check_in_timestamp
		#second = total.seconds
		employee_name = frappe.get_value("Employee", employee , "employee_name")
		#print "converted------------------",type(converted)
		total_working = ""
		if total_lunch != "":
			total_working = total - total_lunch
		else:
			total_working = total
		total_worked = ""
		converted = ""
		
		converted = datetime.timedelta(seconds = total_pots)
		if total_working != "":
			
			total_worked = total_working - converted
		data.append([employee_name, employee,total_worked,location,department,branch,check_in_timestamp,lunch_out_timestamp,lunch_in_timestamp,check_out_timestamp,converted,i])
	return columns, data

def get_columns():
	return [
		_("Employee Name") + "::150",
		_("Employee ID") + ":Link/Employee:150",
		_("Total Hours Signed In") + "::150",
		_("Current Status") + "::150",
		_("Department") + "::150",
		_("Branch") + "::150",
		_("Check In") + "::150",
		_("Lunch Out") + "::180",
		_("Lunch In") + "::150",
		_("Check Out") + "::150",
		_("Total PTO Time Taken") + "::150",
		_("Number of PTOs") + "::150"
		]
def get_attendance_details(employee,date):
	attendance = frappe.get_list("Biometric Attendance", filters={"employee_id":employee, "date":date}, fields=["*"], order_by = "name")
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
