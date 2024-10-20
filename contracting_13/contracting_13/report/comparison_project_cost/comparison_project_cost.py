# Copyright (c) 2023, Dynamic Technology and contributors
# For license information, please see license.txt

import frappe
import itertools 
from frappe import _
from itertools import groupby


def execute(filters=None):
	columns = get_columns(filters) or []
	conditions = get_conditions(filters) or []
	data = get_data(conditions) or []
	# print (f'\n\n\ndata====>{data}\n\n')
	return columns, data


def get_conditions(filters):
	cond = "1=1 " 
	if len(filters):
		if filters.get('from_date'):
			cond += " AND `tabComparison`.creation >= date('%s') "%(filters.get('from_date'))
		if filters.get('to_date'):
			cond += " AND `tabComparison`.creation <= '%s' "%(filters.get('to_date'))
		if filters.get('comparison'):
			cond += " AND `tabComparison`.comparison = '%s' "%(filters.get('comparison'))
		if filters.get('project'):
			cond += " AND `tabGL Entry`.project = '%s' "%(filters.get('project'))
			cond += " AND `tabComparison`.project = '%s' "%(filters.get('project'))
		if filters.get('customer'):
			cond += " AND `tabComparison`.customer = '%s' "%(filters.get('customer'))
	return cond
		# print(f'\n\nfilters={cond}\n\n')
		# # if filters.get

def get_columns(filters):
	columns = [
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 160,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{
			"label": _("Comparison"),
			"fieldname": "comparison",
			"fieldtype": "Link",
			"options": "Comparison",
			"width": 160,
		},
		{
			"label": _("Main Item"),
			"fieldname": "main_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		# {
		# 	"label": _("Main Item Name"),
		# 	"fieldname": "main_item_name",
		# 	"fieldtype": "Link",
		# 	"options": "Item",
		# 	"width": 160,
		# },
		# {
		# 	"label": _("Child Name"),
		# 	"fieldname": "child_name",
		# 	"fieldtype": "Link",
		# 	"options": "Item",
		# 	"width": 160,
		# },
		
		{
			"label": _("Real Cost"),
			"fieldname": "real_cost",
			"fieldtype": "Float",
			"width": 160,
		},
		
	]
	return columns

def get_data(conditions):
	sql = f"""
		SELECT `tabComparison`.name as comparison,`tabGL Entry`.project
		,`tabComparison`.customer
		, `tabComparison`.owner as parent_field
		,`tabComparison Item`.clearance_item as main_item
		,sum(`tabGL Entry`.debit) as real_cost FROM `tabGL Entry` 
		INNER JOIN `tabComparison`
		ON `tabGL Entry`.project=`tabComparison`.project 
		INNER JOIN `tabComparison Item`
		ON `tabComparison`.name=`tabComparison Item`.parent
		WHERE  {conditions}
		GROUP by `tabGL Entry`.project, `tabComparison`.name
		
	"""
	# order by `tabComparison`.name
	# 	limit 1
	# data_ = [
	# 	{'indent':0,'comparison': 'COM-23-12-23-0055', 'project': 'PROJ-0025', 'customer': 'mostafa', 'parent_field': 'Administrator', 'main_item': 'LOW CURRENT EARTHING SYSTEM-0.5 ohm-IT ROOM', 'real_cost': 777777},
	# 	{'indent':1,'comparison': 'COM-23-12-23-0055', 'project': 'PROJ-0025', 'customer': 'mostafa', 'parent_field': 'Administrator', 'main_item': 'LOW CURRENT EARTHING SYSTEM-0.5 ohm-IT ROOM', 'real_cost': 61618000.0},
	# 	{'indent':1,'comparison': 'COM-23-12-23-0077', 'project': 'PROJ-0025', 'customer': 'mostafa', 'parent_field': 'Administrator', 'main_item': 'LOW CURRENT EARTHING SYSTEM-0.5 ohm-IT ROOM', 'real_cost': 61618000.0},
	# 	]
	data = frappe.db.sql(sql,as_dict=1)
	# key_func = lambda x: (x["comparison"], x["main_item"]) 
	# for key, group in groupby(data_, key_func):
	# 	print(f'\n\n==key={key}==>\n\n\n')
	# 	for grp in group:
	# 		print(f'\n\n=grp=={grp}==>\n\n\n')
	return data or []



