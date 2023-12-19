import frappe




def validate_quotation(doc,*args):
    for row in doc.items:
        row.db_set('rate',row.rate_demo)
    frappe.db.commit()