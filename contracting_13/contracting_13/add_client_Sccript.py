import frappe
from frappe.model.mapper import get_mapped_doc
from frappe import _
@frappe.whitelist()
def add_sales_order_script():
	add_properties()
	return





def add_properties():
	try:
		name = "Journal Entry Account-reference_type-options"
		if frappe.db.exists("Property Setter",name) :
			doc = frappe.get_doc("Property Setter",name)
		else :

			doc = frappe.new_doc("Property Setter")

		doc.doc_type  = "Journal Entry Account"
		doc.doctype_or_field = "DocField"
		doc.field_name = "reference_type"
		doc.name = name
		doc.property = "options"
		doc.property_type = "Text"
		doc.value = "\nSales Invoice\nPurchase Invoice\nJournal Entry\nSales Order\nPurchase Order\nExpense Claim\nAsset\nLoan\nPayroll Entry\nEmployee Advance\nExchange Rate Revaluation\nInvoice Discounting\nFees\nPay and Receipt Document\nComparison\nClearance\nTender"

		doc.save()
	except:
		pass



@frappe.whitelist()
def make_clearence(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)

	def set_missing_values(source, target):
		target.flags.ignore_permissions = True
		target.update({'clearance_type': "Outcoming"})
		target.update({'purchase_taxes_and_charges_template':source.taxes_and_charges})
		target.update({'total_after_tax':source.grand_total})

	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Clearance",
			"field_map": {
				"project":"project"
			# 	"customer": "customer",
			},
		},
		"Sales Order Item": {
			"doctype": "Clearance Items",
			"field_map": {
				"item_code":"clearance_item",
				"rate":"price",
				"qty":"qty",
				"qty":"current_qty",
				"amount":"total_price",
				"uom":"uom"
			},
			"add_if_empty": True
		},
		"Sales Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges Clearances",
			"field_map": {
				"charge_type": "charge_type",
				# "account_head": "account_head",
				# "description":"description"
			},
			"add_if_empty": True
		},
	}, target_doc,postprocess, ignore_permissions=ignore_permissions)

	return doclist







@frappe.whitelist()
def make_task_clearence(source_name, target_doc=None, ignore_permissions=False):
	task = frappe.get_doc("Task",source_name)
	if not task.sales_order :
		frappe.throw(_("Please Set Sales Order"))
	clearance = make_clearence(task.sales_order, target_doc, ignore_permissions)
	print ("clearance111111 => ",clearance.items)
	items = clearance.items or []
	clearance.set("items",[])
	print ("clearance11111111111111111 => ",items)
	for task_item in task.items :
		item = [x for x in items if x.clearance_item == task_item.item_code]
		if len(item) > 0 :
			item = item[0]
			item.qty = task_item.qty
			item.clearance_state = task_item.state
			clearance.append("items",item)
	print ("clearance 2222222222 => ",clearance.items)
	return clearance


		
