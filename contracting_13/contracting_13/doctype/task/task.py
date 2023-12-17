import frappe
from frappe import _
from frappe.utils.data import get_link_to_form

@frappe.whitelist()
def create_tasks_from_sales_order(source_name):
    so = frappe.get_doc("Sales Order" , source_name)
    if not so.comparison :
        frappe.throw(_("Sales Order hasn't Comparison"))
    comparison = frappe.get_doc("Comparison" , so.comparison)
    # if not comparison.tender :
    #     frappe.throw(_("Comparison hasn't Tender"))
    tender = frappe.get_doc("Tender" , comparison.tender) if comparison.tender else ''
    tasks = []
    for item in so.items :
        if tender:
            for state in tender.states_template :
                task = frappe.new_doc("Task")
                task.project = so.project
                task.comparison = so.comparison
                task.tender = comparison.tender or ''
                task.sales_order = source_name
                task.subject = f"""{state.state} {item.qty} {item.item_code}:{item.item_name}"""
                task.description = f"""{state.state} {item.qty} {item.item_code}:{item.item_name}"""
                task.set("items",[])
                task.append("items",{
                    "item_code":item.item_code,
                    "item_name":item.item_name,
                    "description":item.description,
                    "state":state.state,
                    "uom":item.uom,
                    "qty":item.qty,
                })
                
                task.save()
                lnk = get_link_to_form(task.doctype,task.name)
                frappe.msgprint(_("{} {} was created.").format(_(task.doctype),lnk))
                tasks.append(task)
        if not tender:
            task = frappe.new_doc("Task")
            task.project = so.project
            task.comparison = so.comparison
            task.tender = comparison.tender or ''
            task.sales_order = source_name
            task.subject = f""" {item.qty} {item.item_code}:{item.item_name}"""
            task.description = f""" {item.qty} {item.item_code}:{item.item_name}"""
            task.set("items",[])
            task.append("items",{
                "item_code":item.item_code,
                "item_name":item.item_name,
                "description":item.description,
                "uom":item.uom,
                "qty":item.qty,
            })
            
            task.save()
            lnk = get_link_to_form(task.doctype,task.name)
            frappe.msgprint(_("{} {} was created.").format(_(task.doctype),lnk))
            tasks.append(task)
    return tasks