import frappe




def validate_quotation(doc,*args):
    for row in doc.items:
        row.db_set('rate',float(row.rate_demo or row.rate))
    frappe.db.commit()