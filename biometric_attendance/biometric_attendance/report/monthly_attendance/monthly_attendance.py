# Copyright (c) 2013, Akshay Mehta and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import datetime
import math
from datetime import timedelta
from frappe.utils import getdate, cint

class DateTimeEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
			return obj.isoformat()
		elif isinstance(obj, datetime.timedelta):
			return (datetime.datetime.min + obj).time().isoformat()

		return super(DateTimeEncoder, self).default(obj)


def execute(filters=None):
	columns, data = [], []

	if filters.get("date_range"):
		filters.update({"from_date": filters.get("date_range")[0], "to_date":filters.get("date_range")[1]})
	else:
		return

	if abs((getdate(filters.get("from_date"))-getdate(filters.get("to_date"))).days) > 31:
		frappe.msgprint("""Date Range Should Not be More than 31 Days""")
		return columns, data

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	columns = [
			{
			  "fieldname": "user_code",
			  "fieldtype": "Link",
			  "options": "Biometric Users",
			  "label": "User Code",
			  "width": 100
			},
			{
			  "fieldname": "user_name",
			  "fieldtype": "Data",
			  "label": "User Name",
			  "width": 150
			},
			{
			  "fieldname": "branch",
			  "fieldtype": "Data",
			  "label": "Branch",
			  "width": 100
			}
	]

	days = getdate(filters.get("to_date")) - getdate(filters.get("from_date"))
	current_date = getdate(filters.get("from_date"))
	for n in range(0, days.days+1):
		build_key = current_date.strftime('%d-%m-%Y')
		if cint(filters.get("detailed_view")):
			ext_col = [
				{
				"fieldtype": "Int",
				"fieldname": build_key+"punch",
				"label": "Punch Count "+build_key
				},
				{
				"fieldtype": "Time",
				"fieldname": build_key+"entry",
				"label": "Entry Time "+build_key
				},
				{
				"fieldtype": "Time",
				"fieldname": build_key+"exit",
				"label": "Exit Time "+build_key
				}
			]
			columns.extend(ext_col)
		ext_col = [
			{
			"fieldtype": "Data",
			"fieldname": build_key+"attendance",
			"label": build_key,
			"default": "A"
			}
		]
		columns.extend(ext_col)
		current_date += timedelta(days=1)
	columns.extend(get_summary_columns())
	columns.extend([{
			  "fieldname": "biometric_attendance",
			  "fieldtype": "Text",
			  "label": "Biometric Dump",
			  "width": 0
			}])
	return columns

def get_summary_columns():
	columns = [
			{
			"fieldtype": "Int",
			"fieldname": "absent",
			"label": "Absent"
			},
			{
			"fieldtype": "Int",
			"fieldname": "halfday",
			"label": "Half Days"
			},
			{
			"fieldtype": "Int",
			"fieldname": "present",
			"label": "Present"
			},
			{
			"fieldtype": "Int",
			"fieldname": "total_present",
			"label": "Total Present (H+P)"
			},
			{
			"fieldtype": "Int",
			"fieldname": "total_off",
			"label": "Total Off Allowed"
			},
			{
			"fieldtype": "Int",
			"fieldname": "leave",
			"label": "Leave Availed"
			},
			{
			"fieldtype": "Int",
			"fieldname": "final_working",
			"label": "Final Working Days"
			}
	]
	return columns

def get_data(filters):
	query = """
		select
		  users.name as `User Code`,
		  users.user_name as `User Name`,
		  users.branch as `Branch`,
		  if(users.differ_timings=1, users.allowed_entry_time, branch.opening_time) as `Opening Time`,
		  if(users.differ_timings=1, users.allowed_exit_time, branch.closing_time) as `Closing Time`,
		  cast(att.timestamp as Date) as `Date`,
		  cast(min(att.timestamp) as time) as `Entry Time`,
		  cast(max(att.timestamp) as time) as `Exit Time`,
		  ifnull(count(*),0) as `Punch Count`,
		  if(timestampdiff(MINUTE,cast(if(users.differ_timings=1,users.allowed_entry_time,branch.opening_time) as Time), cast(min(att.timestamp) as time))<=30, 1, 0) as `On Time Entry`,
		  if(timestampdiff(MINUTE,cast(if(users.differ_timings=1,users.allowed_exit_time,branch.closing_time) as Time), cast(max(att.timestamp) as time))>=-30, 1, 0) as `On Time Exit`
		from
		  `tabBiometric Users` users,
		  `tabBiometric Attendance` att,
		  `tabBranch Settings` branch
		where
		  att.user_id = cast(substring(users.name,3) as Integer)
		  and cast(att.timestamp as Date) >= '{from_date}'
		  and cast(att.timestamp as Date) <= '{to_date}'
		  and branch.branch like '{branch}'
		  and users.branch = branch.branch
		group by
		  `Date`,
		  users.name
		order by
		  `User Code`
	"""

	query = query.format(**{
			"from_date":filters.get("from_date"),
			"to_date": filters.get("to_date"),
			"branch": filters.get("branch") if filters.get("branch") else "%%"
			})

	current_user_name = None
	rows = []
	current_row = {}
	ba = []
	total_A = 0
	total_P = 0
	total_H = 0
	for d in frappe.db.sql(query, as_dict=1):
		if current_user_name != d["User Code"]:
			if current_user_name:
				current_row["biometric_attendance"] = DateTimeEncoder().encode(sorted(ba, key=lambda k: k['Date']))
                        	total_working_days = total_P + math.ceil(total_H/2.0)
				total_weekly_off_allowed = round(total_working_days / 7.0, 0)
				leaves = 0
				if total_A > 0:
					leaves = 1
				current_row["absent"] = total_A
				current_row["halfday"] = total_H
				current_row["present"] = total_P
				current_row["total_present"] = total_working_days
				current_row["total_off"] = total_weekly_off_allowed
				current_row["leave"] = leaves
				current_row["final_working"] = total_weekly_off_allowed + total_working_days + leaves

				rows.append(current_row)
			current_row = {}
			current_user_name = d["User Code"]
			current_row["user_name"] = d["User Name"]
			current_row["user_code"] = d["User Code"]
			current_row["branch"] = d["Branch"]
			ba = []
			total_A = abs((getdate(filters.get("from_date"))-getdate(filters.get("to_date"))).days)+1
			total_P = 0
			total_H = 0

		ba.append(d)
		build_key = d["Date"].strftime('%d-%m-%Y')
		current_row[build_key+"punch"] = d["Punch Count"]
		current_row[build_key+"entry"] = d["Entry Time"]
		current_row[build_key+"exit"] = d["Exit Time"]
		current_row[build_key+"attendance"] = get_final_attendance(d)
		if current_row[build_key+"attendance"] == "P":
			total_P = total_P + 1
			total_A = total_A - 1
		elif current_row[build_key+"attendance"] == "H":
			total_H = total_H + 1
			total_A = total_A - 1

	return rows

def get_final_attendance(record):
	total_time = record['Entry Time'].total_seconds() - record['Exit Time'].total_seconds()
	total_working_time = record['Opening Time'].total_seconds() - record['Closing Time'].total_seconds()
	if abs(total_time/total_working_time) >= .75:
		return "P"
	elif abs(total_time/total_working_time) >= .4 and abs(total_time/total_working_time) < .75:
		return "H"
	else:
		return "A"


def get_biometric_attendance(filters, user=None, employee=None):
	if not user and not employee:
		return

	if user and employee:
		return

	query = """
		select
			  users.name as `User Code`,
			  users.employee as `Employee Code`,
			  users.user_name as `User Name`,
			  users.branch as `Branch`,
			  if(users.differ_timings=1,users.allowed_entry_time,branch.opening_time) as `Branch Opening Time`,
			  if(users.differ_timings=1,users.allowed_exit_time,branch.closing_time) as `Branch Closing Time`,
			  cast(att.timestamp as date) as `Punch Date`,
			  count(*) as `Punch Count`,
			  cast(min(att.timestamp) as Time) as `Earliest Punch`,
			  cast(max(att.timestamp) as Time) as `Last Punch`
		from
			  `tabBiometric Users` users,
			  `tabBiometric Attendance` att,
			  `tabBranch Settings` branch
		where
			  att.user_id = cast(substring(users.name,3) as Integer)
			  and cast(att.timestamp as date) >= %s
			  and cast(att.timestamp as date) <= %s
			  and users.branch = branch.branch
			  {0}
		group by
			  cast(att.timestamp as date),
			  users.name
		order by
			  cast(att.timestamp as date),
			  users.user_name
		""".format(get_user_or_employee(user, employee))

	ba = frappe.db.sql(query, (filters.get("from_date"), filters.get("to_date")), as_dict=1)
	return DateTimeEncoder().encode(ba)

def get_user_or_employee(user, employee):
	if user:
		return """and users.name = '{0}'""".format(user)
	else:
		return """and users.employee = '{0}'""".format(employee)
