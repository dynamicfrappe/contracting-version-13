import frappe

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.stock.get_item_details import (
	_get_item_tax_template,
	get_conversion_factor,
	get_item_details,
	get_item_tax_map,
	get_item_warehouse,
)
from erpnext.stock.doctype.item.item import get_uom_conv_factor

force_item_fields = (
	"item_group",
	"brand",
	"stock_uom",
	"is_fixed_asset",
	"item_tax_rate",
	"pricing_rules",
	"weight_per_unit",
	"weight_uom",
	"total_weight",
)
DOMAINS = frappe.get_active_domains()

class CustomSalesInvoice(SalesInvoice):
	
	def set_missing_item_details(self, for_validate=False):
		if 'Contracting' in DOMAINS:
			"""set missing item values"""
			from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

			if hasattr(self, "items"):
				parent_dict = {}
				for fieldname in self.meta.get_valid_columns():
					parent_dict[fieldname] = self.get(fieldname)

				if self.doctype in ["Quotation", "Sales Order", "Delivery Note", "Sales Invoice"]:
					document_type = "{} Item".format(self.doctype)
					parent_dict.update({"document_type": document_type})

				# party_name field used for customer in quotation
				if (
					self.doctype == "Quotation"
					and self.quotation_to == "Customer"
					and parent_dict.get("party_name")
				):
					parent_dict.update({"customer": parent_dict.get("party_name")})

				self.pricing_rules = []
				for item in self.get("items"):
					if item.get("item_code"):
						# print(f'/n/n/n=item%%%%%%=>{item.get("rate")}--{item.get("price_list_rate")}/n/n/n')
						args = parent_dict.copy()
						args.update(item.as_dict())

						args["doctype"] = self.doctype
						args["name"] = self.name
						args["child_docname"] = item.name
						args["ignore_pricing_rule"] = (
							self.ignore_pricing_rule if hasattr(self, "ignore_pricing_rule") else 0
						)

						if not args.get("transaction_date"):
							args["transaction_date"] = args.get("posting_date")

						if self.get("is_subcontracted"):
							args["is_subcontracted"] = self.is_subcontracted

						ret = get_item_details(args, self, for_validate=True, overwrite_warehouse=False)
						# print(f'/n/n/n=override ****=ret=>{ret}/n/n/n')
						not_check = ['rate','price_list_rate','discount_amount']
						for fieldname, value in ret.items():
							# print(f'/n/n/n==ret=>{fieldname}**{value}/n/n/n')
							if item.meta.get_field(fieldname) and value is not None and fieldname not in not_check:
								# print(f'/n/n/n=ifff=>{fieldname}**{value}/n/n/n')
								if item.get(fieldname) is None or fieldname in force_item_fields:
									item.set(fieldname, value)

								elif fieldname in ["cost_center", "conversion_factor"] and not item.get(fieldname):
									item.set(fieldname, value)

								elif fieldname == "serial_no":
									# Ensure that serial numbers are matched against Stock UOM
									item_conversion_factor = item.get("conversion_factor") or 1.0
									item_qty = abs(item.get("qty")) * item_conversion_factor

									if item_qty != len(get_serial_nos(item.get("serial_no"))):
										item.set(fieldname, value)

								elif (
									ret.get("pricing_rule_removed")
									and value is not None
									and fieldname
									in [
										"discount_percentage",
										"discount_amount",
										"rate",
										"margin_rate_or_amount",
										"margin_type",
										"remove_free_item",
									]
								):
									# reset pricing rule fields if pricing_rule_removed
									item.set(fieldname, value)
							
						#set_custom data
						item.set('rate', item.get("rate"))
						item.set('price_list_rate', item.get("price_list_rate"))
						item.set('discount_amount', 0)
						item.set('margin_rate_or_amount', 0)
						
						# print(f'/n/n/n=item after loast =>{item.__dict__}**/n/n/n')
						if self.doctype in ["Purchase Invoice", "Sales Invoice"] and item.meta.get_field(
							"is_fixed_asset"
						):
							item.set("is_fixed_asset", ret.get("is_fixed_asset", 0))
						default_cost_center = frappe.db.get_value("Company" , frappe.defaults.get_user_default("Company") , "cost_center")
						# Double check for cost center
						# Items add via promotional scheme may not have cost center set
						if hasattr(item, "cost_center") and not item.get("cost_center"):
							item.set(
								"cost_center", self.get("cost_center") or default_cost_center
							)

						if ret.get("pricing_rules"):
							self.apply_pricing_rule_on_items(item, ret)
							self.set_pricing_rule_details(item, ret)
					else:
						# Transactions line item without item code

						uom = item.get("uom")
						stock_uom = item.get("stock_uom")
						if bool(uom) != bool(stock_uom):  # xor
							item.stock_uom = item.uom = uom or stock_uom

						# UOM cannot be zero so substitute as 1
						item.conversion_factor = (
							get_uom_conv_factor(item.get("uom"), item.get("stock_uom"))
							or item.get("conversion_factor")
							or 1
						)

				if self.doctype == "Purchase Invoice":
					self.set_expense_account(for_validate)
		else:
			super().set_missing_item_details()
