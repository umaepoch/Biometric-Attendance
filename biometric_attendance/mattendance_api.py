from __future__ import division
from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
import requests
from datetime import date


@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

@frappe.whitelist()
def create_biometric_attendance(reqData):
	reqData = json.loads(reqData)
	#print "create ba has s called",reqData
	stat = {"docstatus":"","location_status":""}
	#print "reqData json",reqData
	employee_user_id = frappe.db.get_value("Employee", {"name":reqData.get("employee_id")},"user_id")
	user_full_name = frappe.db.get_value("User", {"name":employee_user_id},"full_name")
	is_permitted_location_temp = is_permitted_location(reqData.get("latitude"),reqData.get("longitude"),reqData.get("employee_id"))
	bio_aten = frappe.new_doc("Biometric Attendance")
	bio_aten.user_name = user_full_name
	bio_aten.timestamp = reqData.get("time_stamp")
	convert_date = datetime.datetime.strptime( reqData.get("time_stamp"), '%Y-%m-%d %H:%M:%S')
	bio_aten.date = convert_date.date()
	bio_aten.employee_id = reqData.get("employee_id")
	bio_aten.latitude = reqData.get("latitude")
	bio_aten.longitude = reqData.get("longitude")
	bio_aten.location_name = reqData.get("location")
	bio_aten.address_display = reqData.get("address_str")

	bio_aten.source = "Mobile"
	convert_date = datetime.datetime.strptime( reqData.get("time_stamp"), '%Y-%m-%d %H:%M:%S')
	bio_aten.date = convert_date.date()
	bio_aten.punch_status = reqData.get("punch_status")
	bio_aten.punch = get_punch_status_code(reqData.get("punch_status"))
	bset_doc = frappe.get_single("Biometric Settings")
	bio_aten.gps_accuracy_method = bset_doc.gps_accuracy_method


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
	user_email = frappe.db.get_value("User", {"name":reqData.get("user_name")},"name")
	#print "user_email",user_email
	employee_id = frappe.db.get_value("Employee", {"user_id":user_email},"name")
	#print "employee_id",employee_id
	if(employee_id):
		return employee_id
	else:
		return "NotEmployee"

@frappe.whitelist()
def get_location(reqData):
	#print ("reqData",reqData)
	print("came inside get_location"   )
	reqData = json.loads(reqData)
	bset_doc = frappe.get_single("Biometric Settings")
	precision_val = bset_doc.gps_precision
	precision_val = int(precision_val)
	latitude = round(float(reqData.get("latitude")),precision_val)
	longitude =  round(float(reqData.get("longitude")),precision_val)
	latitude_fl = float(reqData.get("latitude"))
	longitude_fl =  float(reqData.get("longitude"))
	lat_long_dic = frappe.db.sql("""select
									latitude ,logitude,employee,location_name
									from
									`tabPermitted Location`
									where  docstatus =1 and employee= %s""" ,
									(reqData.get("employee_id")), as_dict=1)
	#print("lat_long_dic",lat_long_dic)
	#decimal if start
	if bset_doc.gps_accuracy_method == "Decimal":
		if lat_long_dic :
			loc_name_temp=""
			for lat_long in lat_long_dic:
				latitude_actual = round(lat_long["latitude"],precision_val)
				logitude_actual = round(lat_long["logitude"],precision_val)
				print("latitude_actual:",latitude_actual)
				print("logitude_actual:",logitude_actual)
				print("latitude:",latitude)
				print("longitude:",longitude)
				if latitude_actual == latitude and logitude_actual == longitude :
					#print("location valid")
					loc_name_temp =  lat_long["location_name"]
					return loc_name_temp
			return "InValid"
		else: #no permitted location for this employee
			return "NoLocationSavedForThisEmployee"

	#decimal if end

	#per if start
	if bset_doc.gps_accuracy_method == "Percentage":
		if lat_long_dic :
			loc_name_temp=""
			for lat_long in lat_long_dic:
				is_lat_valid = get_gps_accuracy_percentage (latitude_fl,lat_long["latitude"])
				is_lon_valid = get_gps_accuracy_percentage (longitude_fl,lat_long["logitude"])
				if is_lat_valid and is_lon_valid :
					loc_name_temp =  lat_long["location_name"]
					return loc_name_temp
			return "InValid"
		else: #no permitted location for this employee
			return "NoLocationSavedForThisEmployee"

	#per if end



def get_gps_accuracy_percentage(l_val,l_actaul_val):

	bset_doc = frappe.get_single("Biometric Settings")
	gps_percentage = int(bset_doc.gps_percentage)
	test_field = int(bset_doc.percentage_test_field)
	percentage = gps_percentage / test_field
	c  = (abs((l_actaul_val - l_val) / l_actaul_val ) ) * 100 <= percentage
	print("l_val",l_val,"l_actaul_val",l_actaul_val ,"percentage",percentage ,"c",c)
	return c



def is_permitted_location(latitude,longitude,employee_id):
	bset_doc = frappe.get_single("Biometric Settings")
	precision_val = bset_doc.gps_precision
	precision_val = int(precision_val)
	latitude_fl = float(latitude)
	longitude_fl =  float(longitude)

	lat_long_dic = frappe.db.sql("""select
									latitude ,logitude,employee
									from
									`tabPermitted Location`
									where  docstatus =1 and employee= %s""" ,
									(employee_id), as_dict=1)

	#decimal start
	if bset_doc.gps_accuracy_method == "Decimal":

		latitude = round(latitude_fl,precision_val)
		longitude =  round(longitude_fl,precision_val)
		if lat_long_dic :
			loc_name_temp=""
			for lat_long in lat_long_dic:
				latitude_actual = round(lat_long["latitude"],precision_val)
				logitude_actual = round(lat_long["logitude"],precision_val)
				if latitude_actual == latitude and logitude_actual == longitude :
					return "true"
			return "false"
		else: #no permitted location for this employee
			return "NoLocationSavedForThisEmployee"
	#decimal_end

	#per_start
	if bset_doc.gps_accuracy_method == "Percentage":
		if lat_long_dic :
			loc_name_temp=""
			for lat_long in lat_long_dic:
				is_lat_valid = get_gps_accuracy_percentage (latitude_fl,lat_long["latitude"])
				is_lon_valid = get_gps_accuracy_percentage (longitude_fl,lat_long["logitude"])
				if is_lat_valid and is_lon_valid :
					return "true"
			return "false"
		else: #no permitted location for this employee
			return "NoLocationSavedForThisEmployee"
	#per_end

@frappe.whitelist()
def get_punch_status(employee_id):
	#later we have to remove dynamic punch label by punch codes
	#punch_status_list = frappe.db.sql("""select punch_type,punch_no from `tabPunch Child` where parent  ='P-S-00001'""",as_dict=1)
	last_punch_status = get_last_punch_status(employee_id)
	print("last_punch_status",last_punch_status)
	if last_punch_status == "Check In":
		punch_status_list = ["PTO Out","Lunch Out","Check Out"]
	elif last_punch_status == "PTO In":
		lunchdone = is_punchStatus_done(employee_id,"Lunch In")
		if lunchdone:
			punch_status_list = ["PTO Out","Check Out"]
		else:
			punch_status_list = ["PTO Out","Lunch Out","Check Out"]
	elif last_punch_status == "Lunch In":
		punch_status_list = ["PTO Out","Check Out"]
	elif last_punch_status == "PTO Out":
		punch_status_list = ["PTO In"]
	elif last_punch_status == "Lunch Out":
		punch_status_list = ["Lunch In"]
	elif  last_punch_status == "NO_PUNCH_STATUS" :
		punch_status_list = ["Check In"]
	elif  last_punch_status == "Check Out" :
		punch_status_list = []

	return punch_status_list


def get_last_punch_status(employee_id):
	last_punch_status = "NO_PUNCH_STATUS"
	today_date = utils.today()
	#print "today_date",today_date
	last_punch_status_list = frappe.db.sql("""select name,punch_status,timestamp,date from `tabBiometric Attendance` where date = %s and employee_id = %s order by timestamp desc limit 1""",(today_date,employee_id),as_dict=1)
	if last_punch_status_list:
		last_punch_status = last_punch_status_list[0]["punch_status"]
	return last_punch_status

@frappe.whitelist()
def is_punchStatus_done(employee_id,punch_status):
	today_date = utils.today()
	is_punchStatus_done = frappe.db.sql("""select name,punch_status from `tabBiometric Attendance` where date = %s and employee_id = %s  and punch_status=%s""",(today_date,employee_id,punch_status),as_dict=1)
	#print "is_punchStatus_done",is_punchStatus_done
	if is_punchStatus_done:
		return True
	else:
		return False





def get_punch_status_code(punch_status):
	punch_status_list = get_punch_status_list()
	punch_status_code_temp= "hello"
	if punch_status_list:
		for punch_status_row in punch_status_list:
			if punch_status_row["punch_type"] == punch_status :
				punch_status_code_temp = punch_status_row["punch_no"]
				return punch_status_code_temp
	return punch_status_code_temp

def get_punch_status_list():
	punch_status_list = frappe.db.sql("""select punch_type,punch_no from `tabPunch Child` where parent  ='P-S-00001'""",as_dict=1)
	return punch_status_list

#testing codes



@frappe.whitelist()
def get_punch_status_testing():
	punch_status_list = frappe.db.sql("""select punch_type,punch_no from `tabPunch Child` where parent  ='P-S-00001'""",as_dict=1)
	return punch_status_list
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

@frappe.whitelist()
def get_client_session_timeout():
	bset_doc = frappe.get_single("Biometric Settings")
	s_time = int(bset_doc.matendance_session_timeout)
	if s_time:
		return s_time
	else:
		return 2

@frappe.whitelist()
def device_id_validation_updation(user_id,device_id,action):
	print("from device_id_validation_updation user_id:",user_id,"device_id",device_id,"action",action)
	employee_user_id = frappe.db.get_value("Employee", {"user_id":user_id},"name")
	employee_doc = frappe.get_doc("Employee", employee_user_id)

	if action == "updation" :
		employee_doc.pch_device_id =  device_id
		employee_doc.save(ignore_permissions=True)
		return "updated"
	else:
		if employee_doc.pch_device_id:
			return "true" if device_id == employee_doc.pch_device_id else "false"
		else:
			return "no_device_id"

@frappe.whitelist()
def get_gps_accuracy_percentage_testing(l_val,l_actaul_val):
	percentage = 1 / 1000
	l_val = str(l_val)
	l_actaul_val = str(l_actaul_val)
	l_val = float(l_val)
	l_actaul_val = float(l_actaul_val)

	c  = (abs((l_actaul_val - l_val) / l_actaul_val ) ) * 100 <= percentage
	print("before conerting to per",(l_actaul_val - l_val) / l_actaul_val   )
	print("after conerting to per",((l_actaul_val - l_val) / l_actaul_val ) * 100 )
	left_side_per =  (abs((l_actaul_val - l_val) / l_actaul_val ) ) * 100

	print("l_val",l_val,"l_actaul_val",l_actaul_val ,"left_side_per",left_side_per ,"c",c)
	return "l_val",l_val,"l_actaul_val",l_actaul_val ,"left_side_per",left_side_per ,"c",c


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

