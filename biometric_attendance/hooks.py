# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "biometric_attendance"
app_title = "Biometric Attendance"
app_publisher = "Epoch Consultancy"
app_description = "Integrates Biometric Device Attendance"
app_icon = "octicon octicon-organization"
app_color = "grey"
app_email = "jayram@epochconsulting.com"
app_license = "MIT"
doc_events = {
	"Daily Attendance":{
		"before_submit":"biometric_attendance.biometric_attendance.doctype.daily_attendance.daily_attendance.create_erp_attendance"
	}
}

#login validation for biometric 
on_session_creation = [
	"biometric_attendance.api.login_feed"
]


scheduler_events = {
#	"all": [
#
#		"biometric_attendance.biometric_attendance.auto_import.auto_import",
#		"biometric_attendance.biometric_attendance.api.testing"
#	]
	"cron": {

		"* * * * *": [
	            "biometric_attendance.biometric_attendance.auto_import.auto_import",
		    "biometric_attendance.api.check_attendance_leave_before_time",
		    "biometric_attendance.biometric_attendance.doctype.daily_attendance.daily_attendance.create_attedance"
		     
		    
		],
#		"46 17 * * *": [
#		  
#	            "biometric_attendance.api.check_attendance_leave_before_time",
#		    "biometric_attendance.biometric_attendance.doctype.daily_attendance.daily_attendance.create_attedance"
#		]
	}
}

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/biometric_attendance/css/biometric_attendance.css"
# app_include_js = "/assets/biometric_attendance/js/biometric_attendance.js"

# include js, css files in header of web template
# web_include_css = "/assets/biometric_attendance/css/biometric_attendance.css"
# web_include_js = "/assets/biometric_attendance/js/biometric_attendance.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "biometric_attendance.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "biometric_attendance.install.before_install"
# after_install = "biometric_attendance.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "biometric_attendance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {doc_events = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

#scheduler_events = {
#	"all": [
#		#"biometric_attendance.biometric_attendance.auto_import.auto_import",
#		"biometric_attendance.api.testing"
#	]
# 	"daily": [
# 		"biometric_attendance.tasks.daily"
# 	],
# 	"hourly": [
# 		"biometric_attendance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"biometric_attendance.tasks.weekly"
# 	]
# 	"monthly": [
# 		"biometric_attendance.tasks.monthly"
# 	]
#}

# Testing
# -------

# before_tests = "biometric_attendance.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "biometric_attendance.event.get_events"
# }
