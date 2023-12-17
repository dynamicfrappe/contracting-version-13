
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc

import json
import datetime
import pandas as pd 

@frappe.whitelist()
def create_comparision(source_name, target_doc=None, ignore_permissions=True):
	docs = get_mapped_doc(
			"Quotation",
			source_name,
			{
				"Quotation": {
					"doctype": "Comparison",
					"field_map": {
						"party_name": "customer",
						"transaction_date": "start_date",
						"taxes_and_charges": "purchase_taxes_and_charges_template",
					},
					"validation": {
						"docstatus": ["=", 1],
					},
				},
				"Quotation Item": {
				"doctype": "Comparison Item",
				"field_map": {
					"item_code": "clearance_item",
					"uom": "uom",
					"qty": "qty",
					"rate": "price",
					"amount": "total_price",
					"cost_center": "cost_center",
					"build": "build",

				},
			},
			"Sales Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges Clearances",
				"field_map": {
					"charge_type": "charge_type",
					"account_head": "account_head",
					"rate": "rate",
					"tax_amount": "tax_amount",
					"total": "total",
				},
			},
			},
			target_doc,
			postprocess=None,
			ignore_permissions=ignore_permissions,
		)

	return docs
@frappe.whitelist()
def create_quotation(source_name, target_doc=None, ignore_permissions=True):
	docs = get_mapped_doc(
			"Comparison",
			source_name,
			{
				"Comparison": {
					"doctype": "Quotation",
					"field_map": {
						 "customer":"party_name",
						 "project":"project",
						  source_name: "comparison",
						 "start_date":"transaction_date",
						"purchase_taxes_and_charges_template": "taxes_and_charges",
					},
					"validation": {
						"docstatus": ["=", 1],
					},
				},
			# 	"Comparison Item": {
			# 	"doctype": "Quotation Item",
			# 	"field_map": {
			# 		"clearance_item":"item_code",
			# 		"clearance_item_name":"item_name",
			# 		"clearance_item_description":"description",
			# 		"uom": "uom",
			# 		"qty": "qty",
			# 		"price":"rate",
			# 		# "total_price":"amount",
			# 		"cost_center": "cost_center",
			# 		"build": "build",
			# 	},
			# },
			"Purchase Taxes and Charges Clearances": {
				"doctype": "Sales Taxes and Charges",
				"field_map": {
					"charge_type": "charge_type",
					"account_head": "account_head",
					"rate": "rate",
					"tax_amount": "tax_amount",
					"total": "total",
				},
			},
			},
			target_doc,
			postprocess=None,
			ignore_permissions=ignore_permissions,
		)
	# frappe.errprint(f'docs-->{docs.__dict__}')
	docs.comparison = source_name
	source_doc = frappe.get_doc("Comparison", source_name)
	#get items
	for row in source_doc.item:
		docs.append("items" , {
					"item_code" : row.clearance_item ,
					"item_name" : row.clearance_item_name ,
					"description" : row.clearance_item_description,
					'uom' :row.uom ,
					"qty" : row.qty ,
					"rate" : row.price ,
					"cost_center" : row.cost_center ,
					"build" : row.build
		})
		print(f"Row---- {row.clearance_item_name}  --- {row.total_price} -- {row.price}")
		#get item card
		item_card_name = frappe.db.get_value('Comparison Item Card',{'comparison':row.parent,'item_code':row.clearance_item},['name'] )
		if item_card_name:
			item_card_doc = frappe.get_doc('Comparison Item Card', item_card_name)
		# frappe.errprint(f'item_card-->{item_card_name}')
		#get child item and services for item
			if item_card_doc.items:
				for item in item_card_doc.items:
					docs.append('card_items',{
						'item':item.get("item"),
						'item_name':item.get("item_name"),
						'qty':item.get('qty'),
						'uom':item.get("uom"),
						'reference_item':row.clearance_item,
					})
			if item_card_doc.services:
				for serv in item_card_doc.services:
					docs.append('card_services',{
						'item_code':serv.get("item_code"),
						'item_name':serv.get("item_name"),
						'qty':serv.get('qty'),
						'uom':serv.get("uom"),
						'reference_item':row.clearance_item,
					})
	return docs


@frappe.whitelist()
def get_comparison_item_cards(clearance_item , comparison):
	sql = f"""
	select * from `tabComparison Item Card`  
	inner join `tabComparison Item Card Stock Item`
	ON `tabComparison Item Card Stock Item`.parent = `tabComparison Item Card`.name
	where `tabComparison Item Card`.comparison = '{comparison}'
	 and `tabComparison Item Card`.item_code = '{clearance_item}'
	 and `tabComparison Item Card`.docstatus = 1
	 ORDER BY `tabComparison Item Card Stock Item`.idx 
	"""
	total = 0
	results = None
	if frappe.db.sql(sql,as_dict=1) :
		results = frappe.db.sql(sql,as_dict=1)
		if results[0].total_item_price :
			total = results[0].total_item_price 
		return results or [], total or 0



@frappe.whitelist()
def export_data_to_file_fields(items,colms):
	columns = json.loads(colms)
	items = json.loads(items)
	df = pd.DataFrame(data=items)
	df = df.fillna("N/A")
	timestamp = datetime.datetime.now().strftime("%y%M%d%h%m%s")
	output_filename = f"Item_Cards_{timestamp}.xlsx"
	file_type = "public"
	output_path = frappe.get_site_path(file_type, 'files', output_filename)
	df.to_excel(output_path,na_rep=" ",columns=columns,index=False)    
	file_url = f'/files/' + output_filename
	return {
		"file":df,
		"file_url":file_url
	}

#upload_data
@frappe.whitelist()
def upload_data_comaprsion_item_card(file,colms):
	"""
	dtype='object' to read elemnt as object and not remove leading zero in value
	"""
	pat = file.split('/')
	usecols = json.loads(colms)
	data = pd.read_excel(frappe.get_site_path('private', 'files', str(pat[-1])) ,sheet_name = 0,engine='openpyxl',dtype='object', usecols=usecols)
	data = data.fillna('')
	return get_data(data) 

def get_data(data):
	reponse = []
	# colms:['item','item_name','uom','qty','unit_price','total_amount']
	for  index, row in data.iterrows():
		if row.get('item')  and str(row.get('item')) !='nan':
			item_code = str(row.get('item'))  if str(row.get('item')) !='nan' and row.get('item') else " "
			item_name = row.get('item_name')  if str(row.get('item_name')) !='nan' and row.get('item_name') else " "
			qty = row.get('qty')  if str(row.get('qty')) !='nan' and row.get('qty') else 0
			uom = row.get('uom')  if str(row.get('uom')) !='nan' and row.get('uom') else " "
			unit_price = row.get('unit_price')  if str(row.get('unit_price')) !='nan' and row.get('unit_price') else 0
			total_amount = row.get('total_amount')  if str(row.get('total_amount')) !='nan' and row.get('total_amount') else 0
			# print('\n\n\n=in row=>',row,'\n\n\n')
			valid_item =  validate_item_code(item_code)
			if valid_item:
				if valid_item: #! deleted qty >0
					frappe.errprint(f'valid_item')
					obj = {
						"item" :valid_item , 
						"item_name" : item_name , 
						"qty" :qty ,
						"uom" :uom ,
						"unit_price" :unit_price ,
						"total_amount" :total_amount ,
							}
					reponse.append(obj)
	return reponse

def validate_item_code(item_code) :
    sql =f"""SELECT name FROM `tabItem` 
                            WHERE (item_code = '{item_code}' or name='{item_code}')"""
    item_sql = frappe.db.sql(sql,as_dict =1 )
    if len(item_sql) > 0 and item_sql[0].get("name") :
        return item_code
    else :
        frappe.msgprint(_(f""" Item Code Erro {item_code}"""))