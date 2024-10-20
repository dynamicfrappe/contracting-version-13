# Copyright (c) 2021, Dynamic and contributors
# For license information, please see license.txt

from re import template
from shutil import ignore_patterns
from contracting_13.contracting_13.doctype.comparison_item_log.comparison_item_log import get_last_comparison_item_log
from erpnext.accounts.doctype.account.account import get_account_currency
from erpnext.accounts.party import get_party_account
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder, make_sales_invoice

from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.utils import get_fetch_values
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from frappe.model.mapper import get_mapped_doc
from frappe.utils import (
    DATE_FORMAT,
    add_days,
    add_to_date,
    cint,
    comma_and,
    date_diff,
    flt,
    getdate,
    nowdate,
    get_link_to_form
)
from frappe.utils.data import now_datetime


class Clearance(Document):
	def on_submit(self):
		self.update_comparison_tender()
		self.update_purchase_order()
		self.create_deduction_je()

	def on_cancel(self):
		self.update_purchase_order(cancel=1)
		if self.is_grand_clearance :
			self.cancel_sub_clearances()


	def caculate_totals(self) :
		total_price = 0 
		total_after_tax = 0 
		if self.items :
			for clearence_item in self.items :
				doc = frappe.get_doc("Comparison", self.comparison)
				#caculate item total _amount 
				# 1- get cuarrent percent 
				result = frappe.db.sql(f"""SELECT  percent as state_percent from `tabTender States Template` 
						  WHERE  parent ='{self.comparison}'  
						  and  state = '{clearence_item.clearance_state}'""" , as_dict=1)
				state_percent = 100 
				if result :
					state_percent = result[-1].get("state_percent") or 100
					
					print(state_percent)
				clearence_item.state_percent = state_percent
				clearence_item.total_price = (float(clearence_item.price or 0 ) * (float(state_percent or 0 ) / 100 )) * clearence_item.current_qty
				total_price = total_price + float(clearence_item.total_price or 0)
				total_after_tax = clearence_item.total_price  + total_after_tax
		self.total_after_tax = total_after_tax
		self.total_price = total_price
		self.total = total_price
	def validate(self) :
		total_price = 0 
		total_after_tax = 0 
		self.caculate_totals()
		self.calculate_insurance()	

		if self.item_tax :
			for  i in  self.item_tax :
				i.tax_amount  = (i.rate /100) * self.total
				i.total = i.tax_amount  + self.total
				self.total_after_tax = self.total  + i.tax_amount

	def save(self):
		super(Clearance,self).save()
		if self.is_grand_clearance :
			self.cancel_sub_clearances()
			self.update_sub_clearances()


	# def validate(self):
	# 	self.get_comparison_insurance()

	
	@frappe.whitelist()
	def get_comparison_insurance(self) :
		self.total_insurances = 0
		if getattr(self,'comparison'):
			comparison = frappe.get_doc("Comparison",self.comparison)
			insurances = [x for x in (comparison.insurances or []) if x.type_of_insurance == "Payed in Clearance" and x.pay_method == "Cash" ]
			self.set("insurances",[])
			# frappe.msgprint(str(len(insurances)))
			for item in insurances:
				row = self.append("insurances",{})
				row.incurance_detail = item.incurance_detail
				row.type_of_insurance = item.type_of_insurance
				row.pay_method = item.pay_method
				row.precent = item.precent
				row.amount = ((item.precent or 0)/100) * self.grand_total or 0
				row.vaidation_days = item.vaidation_days
				row.payed_from_account = item.payed_from_account
				row.cost_center = item.cost_center
				row.bank_guarantee = item.bank_guarantee
				row.bank = item.bank
				self.total_insurances += row.amount
			print(f'\n\n\n===>{self.total_insurances}\n\n')


			

	def update_sub_clearances(self):
		if self.is_grand_clearance :
			clearnce_str = ",".join([f"'{x.clearance}'" for x in self.sub_clearance_details])
			sql = f"""
			update tabClearance set is_sub_clearance = 1 , grand_clearance = '{self.name}'
			where name in ({clearnce_str}) and docstatus=1
			"""
			# frappe.msgprint(sql)
			frappe.db.sql(sql)
			frappe.db.commit()
	

	def cancel_sub_clearances(self):
		if self.is_grand_clearance :
			sql = f"""
			update tabClearance set is_sub_clearance = 0 , grand_clearance =''
			where grand_clearance ='{self.name}'
			"""
			frappe.db.sql(sql)
			frappe.db.commit()

	@frappe.whitelist()
	def create_insurance_payment(self,*args,**kwargs):
		from datetime import timedelta, date
		company = frappe.get_doc('Company',self.company)
		for item in self.insurances:
			if not item.invocied:
					if item.pay_method == 'Cash':
						je = self.create_journal_entry(
							debit_account = item.insurance_account , #company.insurance_account_for_others_from_us,
							credit_account = company.default_receivable_account,
							amount = item.amount,
							party_type="Customer",
							party=self.customer,
							credit_party = True,
							company_name = company.name
						)
						lnk = get_link_to_form(je.doctype, je.name)
						# je.docstatus = 1
						je.submit()
						frappe.msgprint("Journal Entry '%s' Created Successfully"%lnk)

						item.invocied = 1
						item.save()
						self.save()
		
	@frappe.whitelist()
	def create_insurance_return(self,*args,**kwargs):
		from datetime import timedelta, date
		company = frappe.get_doc('Company',self.company)
		for item in self.insurances:
			if not item.returned  and item.invocied:
					if item.pay_method == 'Cash':
						je = self.create_journal_entry(
							debit_account = company.default_receivable_account , #company.insurance_account_for_others_from_us,
							credit_account = item.insurance_account,
							amount = item.amount,
							party_type="Customer",
							party=self.customer,
							debit_party = True,
							company_name = company.name
						)
						lnk = get_link_to_form(je.doctype, je.name)
						# je.docstatus = 1
						je.submit()
						frappe.msgprint("Journal Entry '%s' Created Successfully"%lnk)

						item.returned = 1
						item.save()
						self.save()
											
	@frappe.whitelist()
	def create_journal_entry(self,debit_account=None,
							credit_account=None,
							party_type=None,
							party=None,
							debit_party  = False,
							credit_party = False,
							amount=0,
							company_name=None,
							posting_date=nowdate()):

		je = frappe.new_doc("Journal Entry")
		je.posting_date = posting_date
		je.voucher_type = 'Journal Entry'
		je.company = company_name
		#je.remark = f'Journal Entry against Insurance for {self.doctype} : {self.name}'

		###credit
		je.append("accounts", {
			"account": credit_account,
			"credit_in_account_currency": flt(amount),
			"reference_type": self.doctype,
			"party":party if credit_party else None,
			"party_type":party_type if credit_party else None,
			"reference_name": self.name,
			"project": self.project,
		})
		## debit
		je.append("accounts", {
			"account":   debit_account,
			"debit_in_account_currency": flt(amount),
			"reference_type": self.doctype,
			"party":party if debit_party else None,
			"party_type":party_type if debit_party else None,
			"reference_name": self.name
		})
		je.save()

		#lnk = get_link_to_form(je.doctype, je.name)
		return je


		
	# def update_comparison(self):
	#     if self.comparison and self.items and self.clearance_type == "Outcoming":
	#         doc = frappe.get_doc("Comparison", self.comparison)
	#         for clearence_item in self.items:
	#             for comparison_item in doc.item:
	#                 if clearence_item.clearance_item == comparison_item.clearance_item:
	#                     # set previous qty and completed qty in clearence
	#                     clearence_item.previous_qty = comparison_item.completed_qty
	#                     clearence_item.completed_qty = clearence_item.current_qty + \
	#                         clearence_item.previous_qty
	#                     clearence_item.completed_percent = (float(
	#                         clearence_item.completed_qty) / float(clearence_item.qty)) * 100 if clearence_item.qty else 0
	#                     clearence_item.previous_percent = (float(
	#                         clearence_item.previous_qty) / float(clearence_item.qty)) * 100 if clearence_item.qty else 0
	#                     clearence_item.previous_amount = float(
	#                         clearence_item.previous_qty) * float(clearence_item.price)

	#                     # update comparison
	#                     comparison_item.completed_qty += clearence_item.current_qty
	#                     comparison_item.completed_percent = (
	#                         comparison_item.completed_qty / clearence_item.qty) * 100 if clearence_item.qty else 0
	#                     comparison_item.remaining_qty = clearence_item.qty - comparison_item.completed_qty
	#                     comparison_item.remaining_percent = (
	#                         comparison_item.remaining_qty / comparison_item.qty) * 100
	#                     comparison_item.remaining_amount = float(
	#                         comparison_item.remaining_qty) * float(clearence_item.price)

	#                     # update remaining in clearence
	#                     clearence_item.remaining_qty = clearence_item.qty - comparison_item.completed_qty
	#                     clearence_item.remaining_percent = (
	#                         comparison_item.remaining_qty / comparison_item.qty) * 100
	#                     clearence_item.remaining_amount = float(
	#                         comparison_item.remaining_qty) * float(clearence_item.price)

	#         self.save()
	#         doc.save()
	#     else:
	#         pass


	def update_comparison_tender(self):
		# if self.comparison and self.items and self.clearance_type == "Outcoming" and not getattr(self,'is_grand_clearance'):
			doc = frappe.get_doc("Comparison", self.comparison)
			tender_doc = None
			if doc.tender :
				tender_doc = frappe.get_doc("Tender",doc.tender)
			for clearence_item in self.items:
				for comparison_item in doc.item:
					if clearence_item.clearance_item == comparison_item.clearance_item:


						# result = get_item_price(self.comparison,clearence_item.clearance_item,
			      	# 			clearence_item.clearance_state,clearence_item.current_qty) or {}
						result = frappe.db.sql(f"""SELECT  percent as state_percent from `tabTender States Template` 
						  WHERE  parent ='{self.comparison}'  
						  and  state = '{clearence_item.clearance_state}'""" , as_dict=1)
						state_percent = 100 
						if result :
							state_percent = result[-1].get("state_percent") or 100
                  
						completed_percent =( float(state_percent or 0 )  * float(clearence_item.current_qty or 0))\
							 			 /( comparison_item.qty or 1)
						completed_amount = clearence_item.total_price
						# frappe.msgprint(str(state_percent))
						# frappe.throw(str(completed_percent))

						comparison_item.previous_percent = float(completed_percent or  0) + float(completed_percent or 0)
						comparison_item.previous_amount = float(completed_amount or  0 )\
							  +float(comparison_item.previous_amount or 0)

						comparison_item.completed_percent = (comparison_item.completed_percent or 0) + completed_percent 
						comparison_item.completed_amount = (comparison_item.completed_amount or 0) + completed_amount



						comparison_item.remaining_percent = 100- comparison_item.completed_percent 
						comparison_item.remaining_amount = (comparison_item.total_price or 0) - comparison_item.completed_amount

						

						log = frappe.new_doc("Comparison Item Log")
						log.posting_date = now_datetime()
						log.state = clearence_item.clearance_state
						log.state_percent = clearence_item.state_percent
						log.item_code = clearence_item.clearance_item
						log.item_name = clearence_item.clearance_item_name
						log.description = clearence_item.clearance_item_description
						log.uom = clearence_item.uom
						log.qty = clearence_item.current_qty or 0
						log.price = clearence_item.current_price or 0
						log.comparison = doc.name
						log.reference_type = self.doctype
						log.reference_name = self.name
						log.submit()



						clearence_item.previous_percent = log.previous_percent
						clearence_item.previous_amount = log.previous_percent
						clearence_item.previous_qty = log.pervious_qty






						clearence_item.completed_percent = log.completed_percent
						clearence_item.completed_amount = log.completed_amount
						clearence_item.completed_qty = log.completed_qty





						clearence_item.remaining_percent = log.remaining_percent
						clearence_item.remaining_amount = log.remaining_percent
						clearence_item.remaining_qty = log.remaining_qty




					# if tender_doc :
						# for tamplate_item in tender_doc.states_template or [] :
							# if tamplate_item.state == clearence_item.clearance_state:
						# 		tamplate_item.current =  (completed_percent / tamplate_item.percent)*100
						# 		# frappe.msgprint(str(tamplate_item.current))
						# 		tamplate_item.completed = (tamplate_item.completed or 0) + tamplate_item.current
						# 		tamplate_item.remaining = 100 - tamplate_item.completed
								

					
					
						
			self.save()

			doc.save()
			if tender_doc :
				tender_doc.save()
		

	@frappe.whitelist()
	def create_payment_entry(self):
		# if not self.customer:
		# 	return "Please Set Customer"
		company = frappe.db.get_value(
			"Global Defaults", None, "default_company")
		company_doc = frappe.get_doc("Company", company)
		cash_account = frappe.db.get_value('Mode of Payment Account',{'parent':self.mode_of_payment},'default_account') # mode of payment
		# project_account = company_doc.capital_work_in_progress_account
		recivable_account = company_doc.default_receivable_account # customer account
		if self.customer:
			cst_sql_account = f"""SELECT account FROM `tabParty Account` WHERE parent='{self.customer}'"""
			customer_account = frappe.db.sql(cst_sql_account,as_dict=1)[0].get('account') or ''
			recivable_account = customer_account if customer_account else recivable_account
		precision = frappe.get_precision(
			"Journal Entry Account", "debit_in_account_currency")

		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.company = company
		journal_entry.posting_date = nowdate()
		# credit
		credit_row = journal_entry.append("accounts", {})
		credit_row.party_type = "Customer"
		credit_row.account = recivable_account
		credit_row.party = self.customer
		credit_row.cost_center = self.cost_center
		credit_row.project = self.project
		credit_row.credit_in_account_currency = flt(
			self.grand_total, precision)
		credit_row.reference_type = self.doctype
		credit_row.reference_name = self.name
		# debit
		debit_row = journal_entry.append("accounts", {})
		debit_row.account = cash_account
		credit_row.cost_center = self.cost_center
		credit_row.project = self.project
		debit_row.debit_in_account_currency = flt(self.grand_total, precision)
		debit_row.reference_type = self.doctype
		debit_row.reference_name = self.name
		journal_entry.save()
		# journal_entry.submit()
		form_link = get_link_to_form(journal_entry.doctype, journal_entry.name)
		frappe.msgprint("Journal Entry %s Create Successfully" % form_link)

		# # second journal
		# s_journal_entry = frappe.new_doc('Journal Entry')
		# s_journal_entry.company = company
		# s_journal_entry.posting_date = nowdate()
		# # credit
		# s_credit_row = s_journal_entry.append("accounts", {})
		# s_credit_row.account = cash_account
		# s_credit_row.credit_in_account_currency = flt(
		# 	self.grand_total, precision)
		# s_credit_row.reference_type = self.doctype
		# s_credit_row.reference_name = self.name
		# # debit
		# s_debit_row = s_journal_entry.append("accounts", {})
		# s_debit_row.account = recivable_account
		# s_debit_row.party_type = "Customer"
		# s_debit_row.party = self.customer
		# s_debit_row.debit_in_account_currency = flt(
		# 	self.grand_total, precision)
		# s_debit_row.reference_type = self.doctype
		# s_debit_row.reference_name = self.name
		# s_journal_entry.save()
		# form_link = get_link_to_form(journal_entry.doctype, journal_entry.name)
		# frappe.msgprint("Journal Entry %s Create Successfully" % form_link)
		# self.paid=1
		# self.save()
		frappe.db.sql(
			"""update tabClearance set paid=1 where name='%s'""" % self.name)
		frappe.db.commit()

	@frappe.whitelist()
	def can_create_invoice(self, doctype):
		invoice = frappe.db.get_value(
			doctype, {"clearance": self.name, "docstatus": ["<", 2]}, 'name')
		return 0 if invoice else 1

	def create_deduction_je(self):
		if getattr(self, 'deductions') and self.total_deductions:
			if self.clearance_type == "incoming":
				if not self.purchase_order:
					frappe.throw(_("Please set Purchase Order"))
				if not self.supplier:
					frappe.throw(_("Please set Supplier"))
				self.create_deduction_supplier_je()
			if self.clearance_type == "Outcoming":
				if not self.sales_order:
					frappe.throw(_("Please set Sales Order"))
				if not self.customer:
					frappe.throw(_("Please set Customer"))
				self.create_deduction_customer_je()

	def create_deduction_supplier_je(self):
		je = frappe.new_doc("Journal Entry")
		je.posting_date = nowdate()
		je.voucher_type = 'Journal Entry'
		je.company = self.company
		je.remark = f'Deduction against  Supplier {self.supplier} Deduction: ' + \
			self.doctype + " " + self.name
		supplier_account = get_party_account(
			"Supplier", self.supplier, self.company)
		if not supplier_account:
			frappe.throw(
				_("Please Account for supplier {}").format(self.supplier))

		je.append("accounts", {
			"account": supplier_account,
			"account_currency": get_account_currency(supplier_account),
			"debit_in_account_currency": flt(self.total_deductions or 0),
			"party_type": "Supplier",
			"party": self.supplier,
			"reference_type": self.doctype,
			"reference_name": self.name
		})
		for row in self.deductions:
			je.append("accounts", {
				"account": row.account,
				"account_currency": get_account_currency(row.account),
				"credit_in_account_currency": row.amount,
				"cost_center": row.cost_center,
				"project": self.project,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
		je.submit()

	def create_deduction_customer_je(self):
		je = frappe.new_doc("Journal Entry")
		je.posting_date = nowdate()
		je.voucher_type = 'Journal Entry'
		je.company = self.company
		je.remark = f'Deduction against  Customer {self.customer} Deduction: ' + \
			self.doctype + " " + self.name
		customer_account = get_party_account(
			"Customer", self.customer, self.company)
		if not customer_account:
			frappe.throw(
				_("Please Account for Customer {}").format(self.customer))

		je.append("accounts", {
			"account": customer_account,
			"account_currency": get_account_currency(customer_account),
			"credit_in_account_currency": flt(self.total_deductions or 0),
			"party_type": "Customer",
			"party": self.customer,
			"project": self.project,
			"reference_type": self.doctype,
			"reference_name": self.name
		})
		for row in self.deductions:
			je.append("accounts", {
				"account": row.account,
				"account_currency": get_account_currency(row.account),
				"debit_in_account_currency": row.amount,
				"project": self.project,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
		je.submit()

	def update_purchase_order(self, cancel=False):
		if self.purchase_order and self.items and self.clearance_type == "incoming":
			for item in self.items:
				try:
					purchase_order_item = frappe.get_doc(
						"Purchase Order Item", item.purchase_order_item)
					if cancel:
						purchase_order_item.completed_qty -= item.current_qty
					else:
						purchase_order_item.completed_qty += item.current_qty

					purchase_order_item.completed_percent = (
						float(purchase_order_item.completed_qty) / float(purchase_order_item.qty)) * 100
					purchase_order_item.completed_amount = (
						float(purchase_order_item.rate) * float(purchase_order_item.completed_qty))

					if cancel:
						purchase_order_item.remaining_qty = max(
							purchase_order_item.qty, purchase_order_item.qty - purchase_order_item.completed_qty)
					else:
						purchase_order_item.remaining_qty = min(
							0, purchase_order_item.qty - purchase_order_item.completed_qty)

					purchase_order_item.remaining_percent = (
						float(purchase_order_item.remaining_qty) / float(purchase_order_item.qty)) * 100
					purchase_order_item.remaining_amount = (
						float(purchase_order_item.rate) * float(purchase_order_item.remaining_qty))
					purchase_order_item.save()
				except:
					pass



	def calculate_insurance(self) :
		total_insurance = 0 
		if len(self.insurances) > 0 :
			for i in self.insurances :
				if int(i.precent or 0) > 0  :
					#calculate amount 
					i.amount = float(self.total_price) * (float(i.precent) /100)
					total_insurance  = total_insurance + i.amount
		self.total_insurances = total_insurance
		self.total = self.total_price - self.total_insurances


@frappe.whitelist()
def get_item_price(comparison, item_code, clearance_state, qty):
	comparison_doc = frappe.get_doc("Comparison", comparison)
	if comparison_doc:
		items = [
			x for x in comparison_doc.item if x.clearance_item == item_code]
		item_price = 0 if not len(items) else items[0].price
		state_percent = 0
		if comparison_doc.tender:
			tender = frappe.get_doc("Tender", comparison_doc.tender)
			states_template = [
				x for x in tender.states_template if x.state == clearance_state]
			state_percent = 0 if not len(states_template) else states_template[0].percent
			# total_qty = sum([x.qty for x in items]) or 1
			# item_price = item_price * (((flt(qty)/total_qty) * state_percent)/100)

		return {
			"state_percent": state_percent,
			"item_price": item_price
		}


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_state_query(doctype, txt, searchfield, start, page_len, filters):
	print("Wotl temder ")
	return frappe.db.sql("""select state from `tabTender States Template`
		where parent = %(parent)s and state like %(txt)s
		limit %(start)s, %(page_len)s""", {
			'parent': filters.get("parent"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		})

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def comparsion_state_get_state_query(doctype, txt, searchfield, start, page_len, filters):
	print("Wotl COM ")
	return frappe.db.sql("""select state from `tabTender States Template`
		where parent = %(parent)s and state like %(txt)s
		limit %(start)s, %(page_len)s""", {
			'parent': filters.get("parent"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		})
















@frappe.whitelist()
def clearance_make_purchase_invoice(source_name, target_doc=None):
    doc = frappe.get_doc("Clearance", source_name)
    invoice = make_purchase_invoice(doc.purchase_order)
    invoice.set_missing_values()
    invoice.is_contracting = 1
    invoice.clearance = doc.name
    invoice.comparison = doc.comparison
    # invoice.set("items",[])
    for row in doc.items:
        invoice_item = [
            x for x in invoice.items if x.po_detail == row.purchase_order_item]
        if len(invoice_item) > 0:
            invoice_item = invoice_item[0]
            invoice_item.qty = row.current_qty

    try:
        invoice.save(ignore_permissions=1)
    except Exception as e:
        frappe.throw(str(e))
    # invoice.submit()
    # doc.purchase_invoice = pi.name
    # doc.save()
    return invoice


@frappe.whitelist()
def clearance_make_sales_invoice(source_name, target_doc=None):
	doc = frappe.get_doc("Clearance", source_name)
	invoice = make_sales_invoice(doc.sales_order)
	#invoice.set_missing_values()
	invoice.is_contracting = 1
	invoice.clearance = doc.name
	invoice.comparison = doc.comparison
	invoice.set_onload("ignore_price_list", True)
	invoice.taxes = []
	if doc.insurances:
		for insurance_row in doc.insurances:
			row = {
				"charge_type":"Actual",
				"account_head":insurance_row.get("insurance_account"),
				"tax_amount":(-1 * flt(insurance_row.get("amount"))) ,
			}
			invoice.append("taxes",row)
	for row in doc.items:
		invoice_item = [
			x for x in invoice.items if x.item_code == row.clearance_item]
		if len(invoice_item) > 0:
			invoice_item = invoice_item[0]
			invoice_item.qty = row.current_qty
			invoice_item.price_list_rate = row.total_price/row.current_qty
			invoice_item.base_price_list_rate = row.total_price/row.current_qty
			invoice_item.rate = row.total_price/row.current_qty

	try:
		#invoice.save(ignore_permissions=1)
		invoice.set_missing_values(for_validate=False)
	except Exception as e:
		frappe.throw(str(e))
	# doc.purchase_invoice = pi.name
	# doc.save()
	return invoice



@frappe.whitelist()
def create_grand_clearance(source_name, target_doc=None, ignore_permissions=False):
	comparison_name = frappe.db.get_value("Sales Order",source_name,"comparison")
	comparison = frappe.get_doc("Comparison",comparison_name)
	sql = f"""
		select name from tabClearance tc 
		where name not in (select clearance from `tabSales Invoice` si where si.docstatus < 2 and IFNULL(si.clearance,'')<>'')
				and tc.docstatus =1  and clearance_type = 'Outcoming' 
				and is_sub_clearance <> 1
				and is_grand_clearance <> 1
				and comparison = '{comparison.name}'
	"""
	un_invoiced_clearance = frappe.db.sql_list(sql) or []
	if not len(un_invoiced_clearance):
		frappe.throw(_("There is no uninvoiced Clearance"))
	
	clearance_str = ",".join(f"'{x}'"for x in un_invoiced_clearance )
	clearance_items_sql = f"""
			select clearance_item ,clearance_state,state_percent, clearance_item_name , clearance_item_description , cost_center , uom
					, qty ,price, SUM(current_qty) as current_qty , SUM(total_price) as total_price 
			from `tabClearance Items` item 
			where parent in ({clearance_str})
			GROUP BY clearance_item  ,clearance_state
	"""
	clearance_items = frappe.db.sql(clearance_items_sql,as_dict=1) or []
	
	if not len(clearance_items):
		frappe.throw(_("There is no uninvoiced Clearance Items")) 

	clearance = frappe.new_doc("Clearance")
	clearance.company = comparison.company
	clearance.comparison = comparison.name
	clearance.project = comparison.project
	clearance.tender = comparison.tender
	clearance.purchase_taxes_and_charges_template = comparison.purchase_taxes_and_charges_template
	clearance.is_grand_clearance = 1
	clearance.clearance_date = nowdate()
	clearance.clearance_type = "Outcoming"
	clearance.set("items",[])
	clearance.set("item_tax",[])
	clearance.set("sub_clearance_details",[])
	clearance.sales_order = source_name
	for item_row in clearance_items :
		last_log = get_last_comparison_item_log(comparison.name,item_row.clearance_item,item_row.clearance_state )
		clearance.append("items",{
			"clearance_item":item_row.clearance_item,
			"clearance_state":item_row.clearance_state,
			"state_percent":item_row.state_percent,
			"clearance_item_name":item_row.clearance_item_name,
			"clearance_item_description":item_row.clearance_item_description,
			"cost_center":item_row.cost_center,
			"uom":item_row.uom,
			"qty":item_row.qty,
			"price":item_row.price,
			"current_qty":item_row.current_qty,
			"total_price":item_row.total_price,
			"current_price" : (item_row.total_price or 0) / (item_row.current_qty or 1),
			"current_percent" : 0 if not last_log else last_log.completed_percent,
			"current_amount" : 0 if not last_log else last_log.completed_amount,
			"previous_qty" : 0 if not last_log else last_log.previous_qty,
			"previous_percent" : 0 if not last_log else last_log.previous_percent,
			"previous_amount" : 0 if not last_log else last_log.previous_amount,
			"completed_qty" : 0 if not last_log else last_log.completed_qty,
			"completed_percent" : 0 if not last_log else last_log.completed_percent,
			"completed_amount" : 0 if not last_log else last_log.completed_amount,
			"remaining_qty" : 0 if not last_log else last_log.remaining_qty,
			"remaining_percent" : 0 if not last_log else last_log.remaining_percent,
			"remaining_amount" : 0 if not last_log else last_log.remaining_amount,
			
		})
	total_tax = 0
	for tax_row in comparison.taxes :
		# total_tax = total_tax + tax_row.tax_amount 
		clearance.append("item_tax",{
			"category":tax_row.category,
			"add_deduct_tax":tax_row.add_deduct_tax,
			"charge_type":tax_row.charge_type,
			"row_id":tax_row.row_id,
			"included_in_print_rate":tax_row.included_in_print_rate,
			"included_in_paid_amount":tax_row.included_in_paid_amount,
			"account_head":tax_row.account_head,
			"description":tax_row.description,
			"rate":tax_row.rate,
			"cost_center":tax_row.cost_center,
			"account_currency":tax_row.account_currency,
			"tax_amount":tax_row.tax_amount,
			"tax_amount_after_discount_amount":tax_row.tax_amount_after_discount_amount,
			"total":tax_row.total,
			"base_tax_amount":tax_row.base_tax_amount,
			"base_total":tax_row.base_total,
			"base_tax_amount_after_discount_amount":tax_row.base_tax_amount_after_discount_amount,
			"item_wise_tax_detail":tax_row.item_wise_tax_detail 
		})
		
	for row in un_invoiced_clearance :
		clearance.append("sub_clearance_details",{
			"clearance":row
		})

	
	return clearance


# def make_purchase_invoice(source_name, target_doc=None):
# @frappe.whitelist()
# def make_purchase_invoice(source_name, target_doc=None):
# 	return get_mapped_purchase_invoice(source_name, target_doc)
