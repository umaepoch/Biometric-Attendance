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
		
	data.append(["", employee,"","",""])
	return columns, data

def get_columns():
	return [
		_("Employee Name") + "::150",
		_("Employee ID") + ":Link/Employee:150",
		_("Total Hours Signed In") + "::150",
		_("Current Status") + "::150",
		_("Check In") + "::150",
		_("Lunch Out") + ":Currency:180",
		_("Lunch In") + "::150",
		_("Check Out") + "::150",
		_("Total PTO Time Taken") + "::150",
		_("Number of PTOs") + "::150"
		]
def get_attendance_details(employee,date):
	attendance = frappe.get_list("Biometric Attendance", filters={"employee_id":employee, "date":date}, fields=["*"])
	return attendance
def get_prepare_details(details):
	punch_status = frappe.get_all("Punch Child", fields={"*"})
	#print "punch-------------",punch_status
	data = []
	#for d in details:
		
