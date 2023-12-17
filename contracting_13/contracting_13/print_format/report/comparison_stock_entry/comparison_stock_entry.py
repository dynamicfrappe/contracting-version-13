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
			cond += " AND `tabStock Entry`.posting_date >= '%s' "%(filters.get('from_date'))
		if filters.get('to_date'):
			cond += " AND `tabStock Entry`.posting_date <= '%s' "%(filters.get('to_date'))
		if filters.get('comparison'):
			cond += " AND `tabStock Entry`.comparison = '%s' "%(filters.get('comparison'))
		if filters.get('from_warehouse'):
			cond += " AND `tabStock Entry`.from_warehouse = '%s' "%(filters.get('from_warehouse'))
		if filters.get('to_warehouse'):
			cond += " AND `tabStock Entry`.to_warehouse = '%s' "%(filters.get('to_warehouse'))
		if filters.get('stock_entry_type'):
			cond += " AND `tabStock Entry`.stock_entry_type = '%s' "%(filters.get('stock_entry_type'))
		if filters.get('customer'):
			cond += " AND `tabComparison`.customer = '%s' "%(filters.get('customer'))
	return cond
		# print(f'\n\nfilters={cond}\n\n')
		# # if filters.get

def get_columns(filters):
	columns = [
		{
			"label": _("Stock Entry"),
			"fieldname": "stock_entry_name",
			"fieldtype": "Link",
			"options": "Stock Entry",
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
		# 	"label": _("Child Item Name"),
		# 	"fieldname": "child_item_name",
		# 	"fieldtype": "Link",
		# 	"options": "Item",
		# 	"width": 160,
		# },
		{
			"label": _("Comparsion Item Card"),
			"fieldname": "comp_item_card",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		
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
			"label": _("Stock Qty"),
			"fieldname": "stock_qty",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Comparsion Stock Qty"),
			"fieldname": "comparsion_stock_qty",
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
	]
	return columns



def get_data(conditions,filters):
	data = []
	if filters.get('stock_entry_type'):
		data = get_data_on_stock_entry_type(filters)
	else:
		data = get_all(conditions)
	return data

def get_all(conditions):
	sql = f"""
		select 
			`tabStock Entry`.name as stock_entry_name_
			,`tabComparison`.customer as customer
			,`tabComparison`.name as comparison
			,`tabStock Entry`.stock_entry_type 
			,`tabStock Entry Detail`.item_code
			,`tabComparison Item Card Stock Item`.item as child_item_name
			,`tabComparison Item Card`.name as comp_item_card
			,CONCAT(`tabStock Entry Detail`.item_code ,":",`tabStock Entry Detail`.item_name)as child_item
			,`tabStock Entry`.comparison_item as main_item
			,`tabStock Entry`.from_warehouse
			,`tabStock Entry`.to_warehouse
			,(`tabStock Entry Detail`.qty ) as stock_qty
			,1 as  main_item_qty 
			,`tabComparison Item Card`.qty comparsion_qty
			,`tabComparison Item Card Stock Item`.qty as comparsion_stock_qty
			,(`tabComparison Item Card Stock Item`.qty * `tabComparison Item Card`.qty)as total_qty
			,((`tabStock Entry Detail`.qty / (`tabComparison Item Card Stock Item`.qty * `tabComparison Item Card`.qty) )*100) as comp_percent
			,((`tabComparison Item Card Stock Item`.qty * `tabComparison Item Card`.qty) - `tabStock Entry Detail`.qty) as outstand_qty
			,(((`tabComparison Item Card Stock Item`.qty * `tabComparison Item Card`.qty) - `tabStock Entry Detail`.qty)/100) as Outstand_percent
			FROM `tabStock Entry`
				INNER JOIN `tabStock Entry Detail`
					ON `tabStock Entry Detail`.parent=`tabStock Entry`.name	
				INNER JOIN `tabComparison`
					ON `tabComparison`.name=`tabStock Entry`.comparison
				INNER JOIN `tabComparison Item Card`
					ON `tabComparison Item Card`.comparison =`tabStock Entry`.comparison
					AND `tabComparison Item Card`.item_code = `tabStock Entry`.comparison_item 
					AND `tabComparison Item Card`.comparison  = `tabComparison`.name
				INNER JOIN `tabComparison Item Card Stock Item`
					ON `tabComparison Item Card Stock Item`.parent=`tabComparison Item Card`.name 
					AND `tabComparison Item Card Stock Item`.item=`tabStock Entry Detail`.item_code 
			where  `tabComparison Item Card`.docstatus=1   
				AND `tabStock Entry`.docstatus=1 AND {conditions}
			ORDER BY `tabStock Entry`.name
	"""
	data = frappe.db.sql(sql,as_dict=1)
	result = []
	check_headers = []
	key_func = lambda x: (x["main_item"], x['stock_entry_name_'],) 
	for key, group in itertools.groupby(data, key_func):
		if key[1] not in check_headers: # stock entry not add before
			head_row = {'main_item':key[0],'stock_entry_name':key[1],'header':True}
			result.append(head_row)
			check_headers.append(key[1])
		for child in list(group):
			result.append(child)
	# result = sorted(result, key=lambda d: d['stock_entry_name'])  
	# print (f'\n\n\nsorted=={result}\n\n')
	return result or []

def get_data_on_stock_entry_type(filters):
	conditions = " 1=1 "
	if filters.get('stock_entry_type'):
			# stock_entry_type = frappe.db.get_value('Stock Entry Type',filters.get('stock_entry_type'),'purpose')
			conditions += " AND `tabStock Entry`.stock_entry_type = '%s' "%(filters.get('stock_entry_type'))
			sql = f"""
			select `tabStock Entry`.name as stock_entry_name_
			,`tabStock Entry`.stock_entry_type 
			,`tabStock Entry Detail`.item_code
			,`tabComparison`.customer as cst
			,`tabStock Entry`.from_warehouse
			,`tabStock Entry`.to_warehouse
			,sum(`tabStock Entry Detail`.qty ) as stock_qty
			,CONCAT(`tabStock Entry Detail`.item_code ,":",`tabStock Entry Detail`.item_name)as child_item
			,`tabStock Entry`.comparison_item as main_item
			,`tabComparison Item Card Stock Item`.item as child_item_name
			,1 as  main_item_qty 
			,SUM(`tabComparison Item`.qty) comparsion_qty
			,SUM(`tabComparison Item Card Stock Item`.qty) qty
			,(`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty)as total_qty
			,((`tabStock Entry Detail`.qty / (`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty) )*100) as comp_percent
			,((`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty) - `tabStock Entry Detail`.qty) as outstand_qty
			,(((`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty) - `tabStock Entry Detail`.qty)/100) as Outstand_percent
			FROM `tabStock Entry`
			INNER JOIN `tabStock Entry Detail`
			ON `tabStock Entry Detail`.parent=`tabStock Entry`.name	
			INNER JOIN `tabComparison Item Card`
			ON `tabComparison Item Card`.comparison =`tabStock Entry`.comparison
			AND `tabComparison Item Card`.item_code = `tabStock Entry`.comparison_item 
			INNER JOIN `tabComparison Item Card Stock Item`
				ON `tabComparison Item Card Stock Item`.parent=`tabComparison Item Card`.name
				AND `tabComparison Item Card Stock Item`.item=`tabStock Entry Detail`.item_code
			INNER JOIN `tabComparison`
			ON `tabComparison`.name=`tabComparison Item Card`.comparison
			INNER JOIN `tabComparison Item`
			ON `tabComparison Item`.parent=`tabComparison Item Card`.comparison
			where  `tabComparison Item Card`.docstatus=1 and `tabComparison`.docstatus=1
			AND `tabStock Entry`.stock_entry_type='Material Transfer' AND {conditions}
			GROUP BY `tabStock Entry`.stock_entry_type,`tabStock Entry Detail`.item_code,`tabStock Entry`.from_warehouse
			ORDER BY `tabStock Entry`.name desc 
			limit 10
			"""
			data = frappe.db.sql(sql,as_dict=1)
			return data





# dm2 = """
# select `tabStock Entry`.name as stock_entry_name_
# 		,`tabStock Entry`.stock_entry_type 
# 		,`tabStock Entry Detail`.item_code
# 		,`tabComparison`.customer as cst
# 		,CONCAT(`tabStock Entry Detail`.item_code ,":",`tabStock Entry Detail`.item_name)as child_item
# 		,`tabStock Entry`.comparison_item as main_item
# 		,`tabComparison Item Card Stock Item`.item as child_item_name
# 		,`tabStock Entry`.from_warehouse
# 		,`tabStock Entry`.to_warehouse
# 		,(`tabStock Entry Detail`.qty ) as stock_qty
# 		,1 as  main_item_qty 
# 		,`tabComparison Item`.qty comparsion_qty
# 		,`tabComparison Item Card Stock Item`.qty qty
# 		,(`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty)as total_qty
# 		,((`tabStock Entry Detail`.qty / (`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty) )*100) as comp_percent
# 		,((`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty) - `tabStock Entry Detail`.qty) as outstand_qty
# 		,(((`tabComparison Item Card Stock Item`.qty * `tabComparison Item`.qty) - `tabStock Entry Detail`.qty)/100) as Outstand_percent
# 		FROM `tabStock Entry`
# 		INNER JOIN `tabStock Entry Detail`
# 		ON `tabStock Entry Detail`.parent=`tabStock Entry`.name	
# 		INNER JOIN `tabComparison Item Card`
# 		ON `tabComparison Item Card`.comparison =`tabStock Entry`.comparison
# 		AND `tabComparison Item Card`.item_code = `tabStock Entry`.comparison_item 
# 		INNER JOIN `tabComparison Item Card Stock Item`
# 			ON `tabComparison Item Card Stock Item`.parent=`tabComparison Item Card`.name
# 			AND `tabComparison Item Card Stock Item`.item=`tabStock Entry Detail`.item_code
# 		INNER JOIN `tabComparison`
# 		ON `tabComparison`.name=`tabComparison Item Card`.comparison
# 		INNER JOIN `tabComparison Item`
# 		ON `tabComparison Item`.parent=`tabComparison Item Card`.comparison
# 		where  `tabComparison Item Card`.docstatus=1 and `tabComparison`.docstatus=1
# 		AND `tabComparison Item Card Stock Item`.docstatus=1
# 		AND`tabStock Entry`.name='MAT-STE-2023-00009'
# 		ORDER BY `tabStock Entry`.name"""
# dem1=f"""
# 		select `tabStock Entry`.name as stock_entry_name_
# 	,`tabStock Entry`.comparison
# 	,`tabStock Entry`.comparison_item as main_item
# 	,`tabStock Entry`.from_warehouse
# 	,`tabStock Entry`.to_warehouse
# 	,CONCAT(`tabStock Entry Detail`.item_code ,":",`tabStock Entry Detail`.item_name)as child_item
# 	,(`tabStock Entry Detail`.qty / `tabComparison Item`.qty) as qty
# 	,`tabComparison`.customer as cst
# 	,`tabComparison Item`.clearance_item_name as main_item_name
# 	,`tabComparison Item`.qty comparsion_qty
# 	,(`tabStock Entry Detail`.qty ) as total_qty
# 	,((`tabStock Entry Detail`.qty / `tabComparison Item`.qty) / (`tabStock Entry Detail`.qty )) as comp_percent
# 	,((`tabStock Entry Detail`.qty ) - (`tabStock Entry Detail`.qty / `tabComparison Item`.qty)) as outstand_qty
# 	,((`tabStock Entry Detail`.qty ) - (`tabStock Entry Detail`.qty / `tabComparison Item`.qty)) as Outstand_percent
# 	FROM `tabStock Entry`
# 	INNER JOIN `tabStock Entry Detail`
# 	ON `tabStock Entry Detail`.parent=`tabStock Entry`.name
# 	INNER JOIN `tabComparison`
# 	ON `tabComparison`.name=`tabStock Entry`.comparison
# 	INNER JOIN `tabComparison Item`
# 	ON `tabComparison`.name=`tabComparison Item`.parent 
# 	AND `tabComparison Item`.clearance_item=`tabStock Entry`.comparison_item
# 	WHERE `tabStock Entry`.comparison is not null
# 	AND `tabStock Entry`.docstatus=1 AND {conditions}
# 	ORDER BY `tabStock Entry`.name
# 	"""