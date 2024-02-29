import frappe 



@frappe.whitelist()
def get_item_desc(item_code) :
   return frappe.get_value("Item" , item_code , "description")
   