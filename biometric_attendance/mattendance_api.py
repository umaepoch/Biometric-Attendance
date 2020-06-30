from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
import requests


@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

@frappe.whitelist()
def create_biometric_attendance(reqData):
	reqData = json.loads(reqData)
	stat = {"docstatus":"","location_status":""}
	#print "reqData json",reqData
	is_permitted_location_temp = is_permitted_location(reqData.get("latitude"),reqData.get("longitude"),reqData.get("employee_id"))

	bio_aten = frappe.new_doc("Biometric Attendance")
	bio_aten.timestamp = reqData.get("time_stamp")
	bio_aten.employee_id = reqData.get("employee_id")
	bio_aten.source = "Mobile"
	convert_date = datetime.datetime.strptime( reqData.get("time_stamp"), '%Y-%m-%d %H:%M:%S')
	bio_aten.date = convert_date.date()

	if reqData.get("punch_status") == "Check In":
		bio_aten.punch = 0
	if reqData.get("punch_status") == "Check Out":
		bio_aten.punch =1
	if reqData.get("punch_status") == "Lunch Out":
		bio_aten.punch = 2
	if reqData.get("punch_status") == "Lunch In":
		bio_aten.punch = 3
	if reqData.get("punch_status") == "Unknown Punch":
		bio_aten.punch = 10
	bio_aten.punch_status = reqData.get("punch_status")

	if(is_permitted_location_temp == "true"):
		bio_aten.is_permitted_location = "Yes"
		bio_aten.save(ignore_permissions=True)
		bio_aten.submit()
		stat["docstatus"] = "submit"
		stat["location_status"] = "valid"
	elif(is_permitted_location_temp == "false"):
		bio_aten.is_permitted_location = "No"
		bio_aten.save(ignore_permissions=True)
		stat["docstatus"] = "save"
		stat["location_status"] = "invalid"
	elif(is_permitted_location_temp == "NoLocationSavedForThisEmployee"):
		bio_aten.is_permitted_location = "Yes"
		bio_aten.save(ignore_permissions=True)
		bio_aten.submit()
		stat["docstatus"] = "submit"
		stat["location_status"] = "NoLocationSavedForThisEmployee"
	return stat

@frappe.whitelist()
def get_employee_id(reqData):
	#print "reqData",reqData
	reqData = json.loads(reqData)
	user_email = frappe.db.get_value("User", {"full_name":reqData.get("user_name")},"email")
	#print "user_email",user_email
	employee_id = frappe.db.get_value("Employee", {"user_id":user_email},"name")
	#print "employee_id",employee_id
	if(employee_id):
		return employee_id
	else:
		return "NotEmployee"

def is_permitted_location(latitude,longitude,employee_id):
	latitude = round(float(latitude),3)
	longitude =  round(float(longitude),3)
	lat_long_dic = frappe.db.sql("""select
									latitude ,logitude,employee
									from
									`tabPermitted Location`
									where  docstatus =1 and employee= %s""" ,
									(employee_id), as_dict=1)
	#print("lat_long_dic",lat_long_dic)
	if lat_long_dic :
		for lat_long in lat_long_dic:
			if lat_long["latitude"] == latitude and lat_long["logitude"] == longitude :
				#print("location valid")
				return "true"
			else:
				#print("location invalid")
				return "false"

	else :
		#no permitted location saved for this user
		#print("No permitted location data")
		return "NoLocationSavedForThisEmployee"





#testing codes

@frappe.whitelist()
def testing():
	latitude="12.96379934"
	longitude = "77.51019058"
	employee_id= "HR-EMP-000010"
	latitude = round(float(latitude),3)
	longitude =  round(float(longitude),3)
	lat_long_dic = frappe.db.sql("""select
									latitude ,logitude,employee
									from
									`tabPermitted Location`
									where latitude = %s and logitude = %s and docstatus =1 and employee= %s""" ,
									(latitude, longitude,employee_id), as_dict=1)
	#print("lat_long_dic",lat_long_dic)

	if lat_long_dic :
		for lat_long in lat_long_dic:
			if lat_long["latitude"] == latitude and lat_long["logitude"] == longitude :
				#print("sucess lat_long ",lat_long)
				return "true" + " lat:" +str(latitude) +  " long:" + str(longitude)
	else:
		return "false" +"status:"+"NoLocationSavedForThisEmployee"

	return "false"+ "lat " +str(latitude) + " long:" + str(longitude)


"""
user testing
@frappe.whitelist()
def testing():
	userFrappe="jay"

	user_email = frappe.db.get_value("User", {"username":userFrappe},"email")
	#print "testing",testing
	employee_id = frappe.db.get_value("Employee", {"user_id":user_email},"name")
	#print "employee_id",employee_id
	if(employee_id):
		return employee_id
	else:
		return "NotEmployee"
"""
