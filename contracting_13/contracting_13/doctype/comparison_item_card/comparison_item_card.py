# Copyright (c) 2021, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext import get_company_currency, get_default_company
from frappe import _
from erpnext.setup.doctype.brand.brand import get_brand_defaults
from erpnext.stock.get_item_details import (
	get_bin_details,
	get_conversion_factor,
	get_default_cost_center,
	get_reserved_qty_for_so,
)
import json

class ComparisonItemCard(Document):

	def on_cancel(self):
		self.ignore_linked_doctypes = ("Comparison")
		

	def before_submit(self):
		self.calcualte_profit()
			# doc.save()
	def calcualte_profit(self):
		self.result = (self.total_item_cost or 0/ self.qty)
		doc = frappe.get_doc("Comparison",self.comparison)
		if bool(doc):
			for item in doc.item :
				if item.clearance_item == self.item_code:
					if self.margin_percent and self.margin_percent > 0 :
						self.margin_rate = ( float(self.result) * (float(self.margin_percent or 0) /100))
						# self.result = float(self.result) +  foat(self.margin_rate)
					# item.item_cost = self.result
					# item.price = self.result + float(self.margin_rate  or 0 )
					# item.total_price = item.price * item.qty
					item.db_set('item_cost',self.result)
					item.db_set('price',self.result + float(self.margin_rate  or 0 ))
					item.db_set('total_price',item.price * item.qty)
					frappe.db.commit()
					print(f""" 
					'item_cost',{self.result} \n
						'price',self.result + {float(self.margin_rate  or 0 )} \n
						 'total_price',{item.price * item.qty}
					""")
	def validate(self):
		self.validate_qty()
		self.calcualte_profit()
		
	def validate_qty(self):
		if not self.qty:
			self.qty = 1
		# if self.qty > self.qty_from_comparison:
		# 	frappe.throw("""You Cant Select QTY More Than %s"""%self.qty_from_comparison)

	@frappe.whitelist()
	def validat_item(self , item_price , item):
		item_price = frappe.get_doc("Item Price" , item_price) 
		if item_price.item_code == item and item_price.selling == 1:
			return item_price.price_list_rate
		
	@frappe.whitelist()
	def fetch_item_price(self , item):
		item_price = ""
		try :
			item_price = frappe.get_last_doc("Item Price" , filters={"item_code" : item , "price_list" : self.price_list})
			if item_price :
				return item_price.name
		except :
			item_price
			

@frappe.whitelist()
def get_item_details_test(args):
		args = json.loads(args)
		company = get_default_company()
		item = frappe.db.sql(
			"""select i.name, i.stock_uom, i.description, i.image, i.item_name, i.item_group,
				i.has_batch_no, i.sample_quantity, i.has_serial_no, i.allow_alternative_item,
				id.expense_account, id.buying_cost_center
			from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
			where i.name=%s
				and i.disabled=0
				and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
			(company, args.get("item_code"), nowdate()),
			as_dict=1,
		)
		if not item:
			frappe.throw(
				_("Item {0} is not active or end of life has been reached").format(args.get("item_code"))
			)

		item = item[0]
		item_group_defaults = get_item_group_defaults(item.name, company)
		brand_defaults = get_brand_defaults(item.name, company)
		rate,price_list = get_item_price(args.get("item_code")) 
		ret = frappe._dict(
			{
				"uom": item.stock_uom,
				"stock_uom": item.stock_uom,
				"description": item.description,
				"rate":rate,
				"image": item.image,
				"item_name": item.item_name,
				"cost_center": get_default_cost_center(
					args, item, item_group_defaults, brand_defaults, company
				),
				"qty": args.get("qty"),
				"transfer_qty": args.get("qty"),
				"conversion_factor": 1,
				"batch_no": "",
				"actual_qty": 0,
				"basic_rate": 0,
				"serial_no": "",
				"has_serial_no": item.has_serial_no,
				"has_batch_no": item.has_batch_no,
				"sample_quantity": item.sample_quantity,
				"expense_account": item.expense_account,
			}
		)
		return ret


def get_item_price(item_code):
    item_price = 0
    price_list =None
    price_list = frappe.db.get_single_value('Selling Settings','selling_price_list')
    if price_list:
        item_price = frappe.db.get_value('Item Price',{'item_code':item_code,'price_list':price_list,'selling':1},'price_list_rate')
    return [item_price,price_list]
