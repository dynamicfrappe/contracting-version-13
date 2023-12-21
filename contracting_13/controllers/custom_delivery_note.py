
import frappe
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote
from erpnext import get_default_company, get_default_cost_center
from frappe.utils import now, formatdate
from erpnext.accounts.utils import get_account_currency, get_fiscal_years
from frappe import _

DOMAINS = frappe.get_active_domains()

class CustomDeliveryNote(DeliveryNote):
	
	def on_submit(self):
		if 'Contracting' in DOMAINS:
			self.create_gl_entry()
		else:
			self.super().on_submit()


	def create_gl_entry(self):
		gl_entries = []
		company = get_default_company()
		fiscal_years = get_fiscal_years(now(), company=company)
		fiscal_year = fiscal_years[0][0]
		if len(fiscal_years) > 1:
			frappe.throw(
				_("Multiple fiscal years exist for the date {0}. Please set company in Fiscal Year").format(
					formatdate(now())
				)
			)
		else:
			fiscal_year = fiscal_years[0][0]
		
		default_stock_account, cost_goods_sold_account = frappe.db.get_value('Company',company,['default_inventory_account','default_expense_account'])
		gl_entries.append(
			{
			"account": default_stock_account,
			"against": cost_goods_sold_account,
			"posting_date": now(),
			'company': company,
			'voucher_type': self.doctype,
			'voucher_no': self.name,
			"fiscal_year": fiscal_year,
			'debit':  self.total,
			'credit': 0,
			'debit_in_account_currency':  self.total,
			'credit_in_account_currency': 0,
			'is_opening': "No",
			'party_type': None,
			'party': None,
			"cost_center": self.items[0].cost_center,
			}
		)
		gl_entries.append(
			{
			"account": cost_goods_sold_account ,
			"against": default_stock_account,
			"posting_date": now(),
			'company': company,
			'voucher_type': self.doctype,
			'voucher_no': self.name,
			"fiscal_year": fiscal_year,
			'debit':  0,
			'credit': self.total,
			'debit_in_account_currency':  0,
			'credit_in_account_currency': self.total,
			'is_opening': "No",
			'party_type': None,
			'party': None,
			"cost_center": self.items[0].cost_center,
			}
		)
		self.insert_gl(gl_entries)
		

	def insert_gl(self,gl_entries):
		for args in gl_entries:
			gle = frappe.new_doc("GL Entry")
			gle.update(args)
			gle.flags.ignore_permissions = 1
			gle.flags.from_repost = False
			gle.flags.adv_adj = False
			gle.flags.update_outstanding = 'No'
			gle.flags.notify_update = False
			gle.submit()