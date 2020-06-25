# Copyright (c) 2013, Akshay Mehta and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from biometric_attendance.biometric_attendance.zk import ZK

def execute(filters=None):
	columns, data = [], []

	if not filters.get("machine"):
		return columns, data

	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	return [
		{
		  "fieldname": "user_name",
		  "label": "User Name",
		  "fieldtype": "Data",
		  "width": 200
		},
		{
		  "fieldname": "uid",
		  "label": "UID",
		  "fieldtype": "Int"
		},
		{
		  "fieldname": "user_id",
		  "label": "User ID",
		  "fieldtype": "Int"
		}
		]

def get_data(filters):
	machine = filters.get("machine")
	machine_doc = frappe.get_doc("Biometric Machine", machine)

	zk = ZK(machine_doc.ip_domain_address, machine_doc.port)
	conn = None

	rows = []

	try:
		conn = zk.connect()
		users = conn.get_users()
		for u in users:
			rows.append(\
					{\
					  "user_name": u.name,\
					  "uid": u.uid,\
					  "user_id": u.user_id\
					}\
				   )

	except Exception as e:
		frappe.throw(e)
	finally:
		if conn:
			conn.disconnect()

	return rows
