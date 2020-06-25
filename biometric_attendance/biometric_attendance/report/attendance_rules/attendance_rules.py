# Copyright (c) 2013, Akshay Mehta and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	user_id = filters.get("user")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	from_date = str(from_date)+" 00:00:00"
	to_date = str(to_date)+" 23:59:59"
	attendance_record = frappe.db.sql(""" select * from `tabBiometric Attendance` where user_id = %s and timestamp >= %s and timestamp <= %s and docstatus=1""",(user_id,from_date,to_date), as_dict=1)
	#for att in attendance_record:
	
	return columns, data
