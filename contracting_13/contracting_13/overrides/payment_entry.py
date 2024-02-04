


import frappe 
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry 

from frappe.utils import (
	cint,
	comma_and,
	comma_or,
	flt,
	fmt_money,
	get_link_to_form,
	getdate,
	nowdate,
)

class custom_payment_entry(PaymentEntry):
	def validate_journal_entry(self):
		for d in self.get("references"):
			if d.allocated_amount and d.reference_doctype == "Journal Entry":
				sql= """select debit, credit from `tabJournal Entry Account`
					where account = %s and party=%s and docstatus = 1 and parent = %s
					and (reference_type is null or reference_type in ("", "Sales Order", "Purchase Order"))
					"""%(self.party_account, self.party, d.reference_name)
				je_accounts = frappe.db.sql(
					"""select debit, credit from `tabJournal Entry Account`
					where account = %s and party=%s and docstatus = 1 and parent = %s
					and (reference_type is null or reference_type in ("","Comparison", "Sales Order", "Purchase Order"))
					""",
					(self.party_account, self.party, d.reference_name),
					as_dict=True,
				)

				if not je_accounts:
					frappe.throw(
						_(
							"Row #{0}: Journal Entry {1} does not have account {2} or already matched against another voucher"
						).format(d.idx, d.reference_name, self.party_account)
					)
				else:
					dr_or_cr = "debit" if self.payment_type == "Receive" else "credit"
					valid = False
					for jvd in je_accounts:
						if flt(jvd[dr_or_cr]) > 0:
							valid = True
					if not valid:
						frappe.throw(
							_("Against Journal Entry {0} does not have any unmatched {1} entry").format(
								d.reference_name, _(dr_or_cr)
							)
						)

