import frappe




def validate_purchase_invoice(doc,*args):
    if doc.bill_no :
        supplier = frappe.get_doc("Supplier" , doc.supplier)
        sql = f'''
                select 
                    si.supplier_invoice_no
                from
                    `tabSupplier` s 
                inner join 
                    `tabSupplier Invoice` si
                on
                    s.name = si.parent 
                where
                     si.supplier_invoice_no = {doc.bill_no} '''
        data = frappe.db.sql(sql , as_dict = 1)
        if not data :
            supplier.append("supplier_invoice_table" , {"supplier_invoice_no" : doc.bill_no})
            supplier.save()
        frappe.throw("This Supplier Invoice No has been set for this supplier before")