# Copyright (c) 2023, Dynamic Technology and contributors
# For license information, please see license.txt

import frappe
import itertools 
from frappe import _

def execute(filters=None):
	columns = get_columns(filters) or []
	conditions = get_conditions(filters) or []
	data = get_data(conditions,filters) or []
	# print (f'\n\n\ndata====>{data}\n\n')
	return columns, data


def get_conditions(filters):
	cond = "1=1 " 
	if len(filters):
		if filters.get('from_date'):
			cond += " AND `tabMaterial Request`.transaction_date >= '%s' "%(filters.get('from_date'))
		if filters.get('to_date'):
			cond += " AND `tabMaterial Request`.transaction_date <= '%s' "%(filters.get('to_date'))
		if filters.get('comparison'):
			cond += " AND `tabMaterial Request`.comparison = '%s' "%(filters.get('comparison'))
		if filters.get('from_warehouse'):
			cond += " AND `tabMaterial Request`.from_warehouse = '%s' "%(filters.get('from_warehouse'))
		if filters.get('to_warehouse'):
			cond += " AND `tabMaterial Request`.to_warehouse = '%s' "%(filters.get('to_warehouse'))
		if filters.get('stock_entry_type'):
			cond += " AND `tabMaterial Request`.stock_entry_type = '%s' "%(filters.get('stock_entry_type'))
		if filters.get('customer'):
			cond += " AND `tabComparison`.customer = '%s' "%(filters.get('customer'))
	return cond
		# print(f'\n\nfilters={cond}\n\n')
		# # if filters.get

def get_columns(filters):
	columns = [
		{
			"label": _("Material Request"),
			"fieldname": "stock_entry_name",
			"fieldtype": "Link",
			"options": "Material Request",
			"width": 160,
		},
		{
			"label": _("Material Request Type"),
			"fieldname": "material_request_type",
			"fieldtype": "Data",
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
		{
			"label": _("Child Item"),
			"fieldname": "child_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		# {
		# 	"label": _("Child Name"),
		# 	"fieldname": "child_name",
		# 	"fieldtype": "Link",
		# 	"options": "Item",
		# 	"width": 160,
		# },
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Total Qty"),
			"fieldname": "total_qty",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Comparsion Percent"),
			"fieldname": "comp_percent",
			"fieldtype": "Percent",
			"width": 160,
		},
		{
			"label": _("Outstand QTY"),
			"fieldname": "outstand_qty",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Outstand Percent"),
			"fieldname": "Outstand_percent",
			"fieldtype": "Percent",
			"width": 160,
		},
		
		{
			"label": _("FROM Warehouse"),
			"fieldname": "from_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 160,
		},
		{
			"label": _("To Warehouse"),
			"fieldname": "to_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 160,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 160,
		},
	]
	return columns

def get_data(conditions,filters):
	if filters.get('stock_entry_type'):
		...

	sql = f"""
		select `tabMaterial Request`.name as matriala_request_name
	,`tabMaterial Request`.comparison
	,`tabMaterial Request`.status
	,`tabMaterial Request`.material_request_type
	,`tabMaterial Request`.comparison_item as main_item
	,`tabMaterial Request`.set_from_warehouse as from_warehouse
	,`tabMaterial Request`.set_warehouse as to_warehouse
	,CONCAT(`tabMaterial Request Item`.item_code ,":",`tabMaterial Request Item`.item_name)as child_item
	,(`tabMaterial Request Item`.qty / `tabComparison Item`.qty) as qty
	,`tabComparison`.customer as cst
	,`tabComparison Item`.clearance_item_name as main_item_name
	,`tabComparison Item`.qty comparsion_qty
	,(`tabMaterial Request Item`.qty ) as total_qty
	,((`tabMaterial Request Item`.qty / `tabComparison Item`.qty) / (`tabMaterial Request Item`.qty )) as comp_percent
	,((`tabMaterial Request Item`.qty ) - (`tabMaterial Request Item`.qty / `tabComparison Item`.qty)) as outstand_qty
	,((`tabMaterial Request Item`.qty ) - (`tabMaterial Request Item`.qty / `tabComparison Item`.qty)) as Outstand_percent
	FROM `tabMaterial Request`
	INNER JOIN `tabMaterial Request Item`
	ON `tabMaterial Request Item`.parent=`tabMaterial Request`.name
	INNER JOIN `tabComparison`
	ON `tabComparison`.name=`tabMaterial Request`.comparison
	INNER JOIN `tabComparison Item`
	ON `tabComparison`.name=`tabComparison Item`.parent 
	AND `tabComparison Item`.clearance_item=`tabMaterial Request`.comparison_item
	WHERE `tabMaterial Request`.comparison is not null
	AND `tabMaterial Request`.docstatus=0 AND {conditions}
	ORDER BY `tabMaterial Request`.name
	"""
	data = frappe.db.sql(sql,as_dict=1)
	result = []
	check_headers = []
	key_func = lambda x: (x["main_item"], x["cst"],x['matriala_request_name'],x['comparsion_qty']) 
	for key, group in itertools.groupby(data, key_func):
		if key[2] not in check_headers: # stock entry not add before
			head_row = {'main_item':key[0],'customer':key[1],'stock_entry_name':key[2],'qty':key[3],'header':True}
			result.append(head_row)
			check_headers.append(key[2])
		for child in list(group):
			result.append(child)
	return result or []



